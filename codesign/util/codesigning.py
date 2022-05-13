import shutil
import tempfile
from pathlib import Path
from subprocess import CompletedProcess
from typing import Final

from lxml import etree
# noinspection PyProtectedMember
from lxml.etree import _Element as etree_Element
# noinspection PyProtectedMember
from lxml.etree import _ElementTree as etree_ElementTree

from util import processes
from util.logging import LOGGING

logger = LOGGING.getLogger(__name__)


def run_codesign_command(
        path_to_item: Path,
        identity: str,
        args: list = None) -> CompletedProcess | CompletedProcess[str]:
    """ Wrapper function which runs the main Apple 'codesign' command.

    :param path_to_item: Path to the file or bundle being signed
    :param identity: Name (aka identity) of an installed codesigning-certificate
    :param args: More arguments, for example '--deep', '--force', '--options=runtime', '--entitlements'
    :return: CompletedProcess instance, containing returncode, stdin, stdout
    """
    if args is None: args = []

    command = ['codesign', '--verbose']
    [command.append(arg) for arg in args if arg]
    command.append('--sign')
    command.append(identity)
    command.append(path_to_item)

    # Note: The macOS 'codesign' command will return a different value than 0 when failed.
    # This in turn will lead to an exception with the error message that 'codesign'
    # returned in run_subprocess(), which we intentionally do NOT catch to fail early.
    result = processes.run_subprocess(command)

    # If we have gotten this far, the 'codesign' command has been successful
    logger.debug('✔️ SIGNED: %s', result.stdout.strip())

    return result


def run_codesign_command_for_hardened_runtime(
        path_to_plist: Path,
        path_to_item: Path,
        identity: str,
        args: list = None) -> CompletedProcess | CompletedProcess[str]:
    """ Wrapper function which runs the main Apple 'codesign' command.

    :param path_to_plist: Path to the plist file which holds properties for hardened runtime
    :param path_to_item: Path to the file or bundle being signed
    :param identity: Name (aka identity) of an installed codesigning-certificate
    :param args: More arguments, for example '--deep', '--force', '--options=runtime', '--entitlements'
    :return: CompletedProcess instance, containing returncode, stdin, stdout
    """
    if args is None: args = []

    command = ['codesign', '--verbose', '--deep']
    [command.append(arg) for arg in args if arg]
    command.append('--sign')
    command.append(identity)
    command.append('--options=runtime')
    command.append('--entitlements')
    command.append(path_to_plist)
    command.append(path_to_item)

    # Note: The macOS 'codesign' command will return a different value than 0 when failed.
    # This in turn will lead to an exception with the error message that 'codesign'
    # returned in run_subprocess(), which we intentionally do NOT catch to fail early.
    result = processes.run_subprocess(command)

    # If we have gotten this far, the 'codesign' command has been successful
    logger.debug('✔️ SIGNED hardened: %s', result.stdout.strip())

    return result


def run_remove_codesign_command(path_to_item: Path):
    """ Removes signature from given file or bundle.

    :param path_to_item: Path to file or bundle from which to remove the signature
    """
    processes.run_subprocess(['codesign', '--remove-signature', path_to_item])
    logger.debug('Removed signature for "%s"', path_to_item)


def create_entitlements_plist(entitlements: dict) -> Path:
    """ Adds entitlements for hardened runtime and re-signs the bundle
    located at 'self.path_to_app_bundle'.
    NOTE: The caller is responsible for removing the (parent) temp dir after using it.

    :param entitlements: Dictionary containing the entitlements which go into the created .plist file
    :return: Path to the temporary created 'entitlements.plist' within a TemporaryDirectory.
    """
    encoding: Final[str] = 'utf-8'
    temp_dir: Final[Path] = Path(tempfile.mkdtemp())
    path_to_plist: Final[Path] = temp_dir / 'entitlements.plist'

    # Create a temporary directory and define path to file entitlements.plist being created.
    try:
        root: etree_Element = etree.fromstring('<plist version="1.0"/>')
        plist: etree_ElementTree = etree.ElementTree(root)
        top_element: etree_Element = etree.SubElement(root, 'dict')

        for key, value in entitlements.items():
            top_element.append(etree.fromstring(f'<key>{key}</key>'))

            if isinstance(value, str):
                top_element.append(etree.fromstring(f'<string>{value}</string>'))

            elif isinstance(value, bool):
                top_element.append(etree.fromstring(f'{"<true/>" if value else "<false/>"}'))

            else:
                raise NotImplementedError(f'Value type {type(value)} not implemented yet')

        # Write changes to file and conform to plist format
        plist.write(str(path_to_plist), encoding='utf8', xml_declaration=True)
        convert_to_plist_format(path_to_plist)

        # Do some debug logging
        persisted_plist: etree_ElementTree = etree.parse(str(path_to_plist))
        logger.debug('Generated entitlement.plist is:\n%s',
                     etree.tostring(persisted_plist, pretty_print=True).decode(encoding))

    except Exception as exc:
        shutil.rmtree(temp_dir, ignore_errors=True)  # remove dir in case something went wrong
        raise exc from None  # re-raise

    return path_to_plist


def convert_to_plist_format(path_to_plist: Path):
    """ Converts XML file to plist format (re-writing the file). Will add DOCTYPE etc.

    :param path_to_plist: Path to the origin plist file which was re-written using an XML parser.
    """
    processes.run_subprocess(['plutil', '-convert', 'xml1', path_to_plist])


def remove_extended_attributes(path_to_item: Path):
    """ Recursively removes extended attributes from a file or directory.

    :param path_to_item: Path to the file or bundle for which to call xattr -r
    """
    processes.run_subprocess(['xattr', '-cr', path_to_item])
    logger.debug('Recursively removed extended attributes from %s', path_to_item)


def run_install_name_tool(source: Path, _from: str, _to: str = None) -> CompletedProcess | CompletedProcess[str]:
    """ install_name_tool changes the dynamic shared library install names
    recorded in a Mach-O binary.
    See also: https://www.unix.com/man-page/osx/1/install_name_tool/

    :param source: Binary executable which must be informed to use a different path to an item
    :param _from: Old path of the item which is referenced by the binary executable
    :param _to: New path of the item which will be referenced by the binary executable
    :return: CompletedProcess instance, containing returncode, stdin, stdout
    """
    command: list

    if not _to:
        command = ['install_name_tool', '-id', f"'{_from}'", source.resolve()]
    else:
        command = ['install_name_tool', '-change', f"'{_from}'", f"'{_to}'", source.resolve()]

    logger.info('Running install_name_tool ...')
    result = processes.run_subprocess(command)  # may raise on error
    logger.info('✅ Finished running install_name_tool')
    logger.debug('install_name_tool results: %s', result.stdout.strip())

    return result
