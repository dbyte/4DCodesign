import shutil
from pathlib import Path
from typing import Final

from lxml import etree
# noinspection PyProtectedMember
from lxml.etree import _Element as etree_Element
# noinspection PyProtectedMember
from lxml.etree import _ElementTree as etree_ElementTree

from core.codesign_config import CodesignConfig
from util import codesigning
from util.logging import LOGGING

logger = LOGGING.getLogger(__name__)


class Codesign:
    # noinspection GrazieInspection
    """ Handles complete codesign / re-sign for macOS 4D *.app bundles (Standalone, Client, Server).
                |
            Ported from Keisuke Miyako's 4D code at
            https://github.com/miyako/4d-class-build-application/blob/main/Project/Sources/Classes/SignApp.4dm
            to Python.
            Note: Signing mobile applications is not yet implemented/ported.
                |
            Normally, 4D's built-in function for signing is sufficient. However, if things change
            in the *.app bundles AFTER the 4D-internal BUILD APPLICATION() has been run, this invalidates
            the macOS signature.
                |
            In addition, plugins, components, etc. which may not have been correctly signed before
            BUILD APPLICATION() was called, can still be signed here on a granular base.
            At the moment (4D v19 R4) there also seems to be an issue with codesigning of two
            (4D-internal) arm64 libs:

            '*.app/Contents/Database/Libraries/lib4d-arm64.dylib'
            and
            '*.app/Contents/Server Database/Libraries/lib4d-arm64.dylib'

            which apparently are not correctly signed by 4D in the built-in signature process.
            Therefore, unfortunately, this module is currently (4D v19 R4) still necessary, but we've disabled
            most functionalities by configuration for our needs. Feel free to enable them in method
            CodesignConfig.runnerOptions
            """

    def __init__(self, config: CodesignConfig):
        self.__config: CodesignConfig = config

    @property
    def config(self) -> CodesignConfig:
        """
        :return: Public codesigning configuration
        """
        return self.__config

    def run(self):
        """ Launches the complete signing process for the given application bundle,
        located at CodesignConfig.path_to_app_bundle.
        """
        logger.info('Running codesign process for application "%s"',
                    self.config.path_to_app_bundle.name)

        self.config.validate()  # fail early if things were not configured as expected
        opts: dict = self.config.runner_options

        # Run the complete signing mechanism for the app.
        # Order of sequence is important (usually bottom-up).

        if opts.get('removeTempFiles'): self.remove_temp_files()
        if opts.get('preCleanup'): self.pre_cleanup()

        if opts.get('signHelpers'): self.sign_helpers()
        if opts.get('signNativeComponents'): self.sign_native_components()
        if opts.get('signUpdater'): self.sign_updater()  # server only
        if opts.get('signFrameworks'): self.sign_frameworks()
        # not implemented   if opts.get('signMobile'): self.sign_mobile()
        if opts.get('signInternalComponents'): self.sign_internal_components()
        if opts.get('removeComponentPlugins'): self.remove_component_plugins()
        if opts.get('signPlugins'): self.sign_plugins()
        if opts.get('signComponents'): self.sign_components()

        # Miyako's target file suffixes in original code for signing the 'Database' dirs:
        # ['.html', '.json', '.js', '.dylib'].
        #
        # We are using a reduced set of target files to prevent overhead - in particular,
        # we only target lib4d-arm64.dylib files - 4D does not sign them correctly (as of 4D v19 R4).
        # Maybe this is an issue of "R" releases only.
        # Also note that this reduced file-set only works if we do not change the 'Database' dirs
        # after 4D signed the applications. Otherwise, use Miyako's original set of suffixes as listed above.
        if opts.get('signDatabase'): self.sign_database(suffixes=['.dylib'])

        if opts.get('signMecab'): self.sign_mecab()  # Japanese
        if opts.get('signSASLPlugins'): self.sign_sasl_plugins()
        if opts.get('signContents'): self.sign_contents()
        if opts.get('removePHP'): self.remove_php()
        if opts.get('signPHP'): self.sign_php()
        if opts.get('signBinDirectory'):  self.sign_bin_dir()  # Some custom 'bin' directory

        self.sign_app()

        logger.info('✅🏆🥂 SUCCESS running codesign process for application "%s"',
                    self.config.path_to_app_bundle.name)

    def remove_temp_files(self):
        """ Removes temporary codesigning files, possibly created after abort
        """
        glob_pattern: Final[str] = '*.cstemp'
        logger.debug('Removing temporary files matching the globbing pattern "%s"', glob_pattern)

        [file.unlink() for file in Path(self.config.path_to_app_bundle).rglob(glob_pattern)]

        logger.debug('✅ finished removing temporary files "%s"', glob_pattern)

    def pre_cleanup(self):
        """ Actually removes signatures from the app bundle and some nested stuff.
        """
        app: Path = self.config.path_to_app_bundle

        logger.info('Running pre-cleanup ... ')

        # Inner helper for convenience: Removes extended attributes and signatures for given item
        def clean(item: Path):
            codesigning.remove_extended_attributes(item)
            codesigning.run_remove_codesign_command(item)

        # Remove signatures for main app bundle
        clean(app)

        # Remove signatures for Native Components when signing option is enabled for them
        if self.config.runner_options.get('signNativeComponents'):
            native_components: Path = app / 'Contents/Native Components'
            [clean(component) for component in native_components.glob('*')]

        logger.info('✅ Finished running pre-cleanup (removed signatures)')

    def sign_helpers(self):
        """ Signs HelperTool, InstallTool, LaunchService
        """
        app: Path = self.config.path_to_app_bundle
        item: Path

        def sign_hardened():
            if item.exists():
                self.codesign(item, hardened_runtime=True, force=True)

        logger.info('Signing 4D helpers ...')

        # Order of sequence is important (usually bottom-up)
        item = app / 'Contents/MacOS/HelperTool'
        sign_hardened()
        item = app / 'Contents/MacOS/InstallTool'
        sign_hardened()
        item = app / 'Contents/MacOS/InstallTool.app/Contents/Library/LaunchServices/com.4D.Helper'
        sign_hardened()
        item = app / 'Contents/MacOS/InstallTool.app'
        sign_hardened()

        logger.info('✅ Finished signing 4D helpers')

    # FIXME: Although everything is correctly notarized by Apple later on,
    #   there is a problem with this method: The app cannot establish connections to external websites
    #   and the macOS 'Activities' App shows the process 'ReportCrash', which causes the processor to glow.
    def sign_native_components(self):
        """ Mainly deep-signs WebViewerCEF.bundle and its frameworks, then resigns all other
        bundles, then re-signs directory 'Native Components' and their frameworks (bottom-up).
            |
        WARNING: Use is not recommended! Although everything is correctly notarized by Apple later on,
        there is a problem with this action: The app cannot establish connections to external websites
        and the macOS 'Activities' App shows the process 'ReportCrash', which goes completely crazy and
        causes the processor to glow.
            |
        Maybe our port of the original 4D-code is buggy here.
        """

        def sign_hardened():
            if item.exists():
                self.codesign(item, hardened_runtime=True, force=True)

        logger.info('Signing native components ...')

        item: Path
        app: Path = self.config.path_to_app_bundle
        native_components: Path = app / 'Contents/Native Components'
        webviewer_bundle: Path = native_components / 'WebViewerCEF.bundle'
        webviewer_helper_app: Path = webviewer_bundle / 'Contents/Frameworks/4D Helper.app'
        webviewer_helper_executable: Path = webviewer_helper_app / 'Contents/MacOS/4D Helper'
        webviewer_helper_frameworks: Path = webviewer_bundle / 'Contents/Frameworks'
        webviewer_chromium_framework: Path = webviewer_helper_frameworks / 'Chromium Embedded Framework.framework'
        webviewer_chromium_framework_libs: Path = webviewer_chromium_framework / 'Libraries'

        # Order of sequence is important (usually bottom-up)

        # 1) ------------------
        # Sometimes, there is a framework folder at
        # <*.app>/Contents/Native Components/WebViewerCEF.bundle/Contents/Frameworks/4D Helper.app/Contents/Frameworks
        # Symlink here will prevent codesign, so delete it.

        special_framework_dir: Path = webviewer_helper_app / 'Contents/Frameworks'

        if special_framework_dir.exists() and special_framework_dir.is_dir():
            # Delete that 'Frameworks' directory which encloses the symlink to "Chromium Embedded Framework.framework"
            shutil.rmtree(special_framework_dir)
            logger.info('Removed special framework dir from native component: "%s"',
                        special_framework_dir)

            # Seems that the following use of run_install_name_tool tells the
            # binary executable to link directly to the Chromium Framework located at:
            # "<*.app>/Contents/Native Components/WebViewerCEF.bundle/Contents/Frameworks/
            # Chromium Embedded Framework.framework"

            # instead of the (the above removed) symlink:

            # "<*.app>/Contents/Native Components/WebViewerCEF.bundle/Contents/Frameworks/4D Helper.app/Contents/
            # Frameworks/Chromium Embedded Framework.framework"
            item = webviewer_helper_executable
            _from: str = '@executable_path/../Frameworks/Chromium Embedded Framework.framework/' \
                         'Chromium Embedded Framework'
            _to: str = '@executable_path/../../../../Frameworks/Chromium Embedded Framework.framework/' \
                       'Chromium Embedded Framework'

            codesigning.run_install_name_tool(source=item, _from=_from, _to=_to)
            self.codesign(item, hardened_runtime=False, force=True)

        # 2) ------------------
        # Sign nested apps within webviewer

        item = webviewer_helper_frameworks / '4D Helper (Plugin).app'
        sign_hardened()
        item = webviewer_helper_frameworks / '4D Helper (GPU).app'
        sign_hardened()
        item = webviewer_helper_frameworks / '4D Helper (Renderer).app'
        sign_hardened()
        item = webviewer_helper_frameworks / '4D Helper.app'
        sign_hardened()

        # 3) ------------------
        # Sign dynamic libraries within Chromium Embedded Framework recursively first

        for item in webviewer_chromium_framework_libs.rglob('*'):
            if not item.name.startswith('.'):
                self.codesign(item, hardened_runtime=False, force=True)

        # Sign Chromium Embedded Framework itself next
        self.codesign(webviewer_chromium_framework, hardened_runtime=False, force=True)

        # 4) ------------------
        # Sign these top-level bundles of the 'Native Components' dir without hardened runtime;
        # Comment in origin code/Miyako: "don't use '--deep', otherwise 4D Helper will become invalid"

        for item in native_components.glob('*'):
            self.codesign(item, hardened_runtime=False, force=False)

        logger.info('✅ Finished signing native components')

    def sign_updater(self):
        """ Signs Updater.app and its frameworks
        """
        app: Path = self.config.path_to_app_bundle

        logger.info('Signing 4D updater ...')

        # Order of sequence is important (usually bottom-up)
        if (updater_frameworks := app / 'Contents/Resources/Updater/Updater.app/Contents/Frameworks').exists():
            for item in updater_frameworks.rglob('*'):
                if not item.name.startswith('.'):
                    self.codesign(item, hardened_runtime=False, force=True)

        if (updater_app := app / 'Contents/Resources/Updater/Updater.app').exists():
            # Sign with hardened runtime because this is an app
            self.codesign(updater_app, hardened_runtime=True, force=True)

        logger.info('✅ Finished signing 4D updater')

    def sign_frameworks(self):
        """ Signs top-level items of the 'Frameworks' directory.
        """
        if (frameworks := self.config.path_to_app_bundle / 'Contents/Frameworks').exists():
            logger.info('Signing frameworks ...')

            for item in frameworks.glob('*'):
                self.codesign(item, hardened_runtime=False, force=True)

            logger.info('✅ Finished signing frameworks')

    def sign_mobile(self):
        raise NotImplementedError('Signing for 4D mobile not implemented')

    def sign_internal_components(self):
        """ Signs recursively all items, filtered by some given suffixes
        within the 'Internal Components' directory.
        """
        accepted_suffixes = ['.html', '.htm', '.json', '.js', '.dylib']

        if (internal_components := self.config.path_to_app_bundle / 'Contents/Resources/Internal Components').exists():
            logger.info('Signing 4D internal components ...')

            for item in internal_components.rglob('*'):
                if not item.name.startswith('.') and item.suffix in accepted_suffixes:
                    self.codesign(item, hardened_runtime=False, force=True)

            logger.info('✅ Finished signing 4D internal components')

    def remove_component_plugins(self):
        """ Looks for item(s) 'Plugins' exactly one level under each found
        component and deletes it/them.
        """
        logger.info('Removing component plugins ...')

        def remove(path: Path):
            # Just an inner convenience function
            shutil.rmtree(path)
            logger.info('Removed "Plugins" directory within component "%s"', path.parent.name)

        # Remove
        folders_to_remove = Path(self.config.path_to_app_bundle / 'Contents/Components').glob(
            '*/Plugins')
        [remove(folder) for folder in folders_to_remove]

        logger.info('✅ Finished removing component plugins')

    def sign_plugins(self):
        """ Signs each plugin (and optionally moves its manifest.json)
        """
        app: Path = self.config.path_to_app_bundle

        if (plugins_dir := app / 'Contents/Plugins').exists():
            logger.info('Signing 4D plugins ...')

            for plugin in plugins_dir.glob('*.bundle'):

                if (manifest := plugin / 'Contents/manifest.json').exists():

                    if self.config.runner_options.get('movePluginManifest'):
                        destination: Path = manifest.parent / 'Resources' / manifest.name
                        shutil.move(src=manifest, dst=destination)
                        logger.info('✔️ Moved plugin manifest from "%s" to "%s"', manifest,
                                    destination)
                        manifest = destination

                    self.codesign(manifest, hardened_runtime=True, force=True)

                self.codesign(plugin, hardened_runtime=False, force=True)

            logger.info('✅ Finished signing 4D plugins')

    def sign_components(self):
        """ Signs recursively all items with suffix .html, .json, .js, .dylib
        within the 'Components' directory.
        """
        accepted_suffixes = ['.html', '.htm', '.json', '.js', '.dylib']

        if (components := self.config.path_to_app_bundle / 'Contents/Components').exists():
            logger.info('Signing 4D components ...')

            for item in components.rglob('*'):
                if not item.name.startswith('.') and item.suffix in accepted_suffixes:
                    self.codesign(item, hardened_runtime=False, force=True)

            logger.info('✅ Finished signing 4D components')

    def sign_database(self, suffixes: list[str]):
        """ Signs recursively all items with suffix .html, .json, .js, .dylib
        within the 'Database' or 'Server Database' directory.

        :param suffixes: List of file extensions to which signing should be applied
            Example: ['.html', '.dylib']
        """
        logger.info('Signing 4D database directory ...')

        app_contents_dir: Path = self.config.path_to_app_bundle / 'Contents'
        database_dirs: list[Path] = [app_contents_dir / 'Database',
                                     app_contents_dir / 'Server Database']

        for database_dir in database_dirs:
            if database_dir.exists():
                for item in database_dir.rglob('*'):
                    if not item.name.startswith('.') and item.suffix in suffixes:
                        self.codesign(item, hardened_runtime=False, force=True)

        logger.info('✅ Finished signing 4D database directory')

    def sign_mecab(self):
        """ Signs mecab bundle if exists
        """
        if (mecab_bundle := self.config.path_to_app_bundle / 'Contents/Resources/mecab/mecab.bundle').exists():
            logger.info('Signing mecab bundle ...')
            self.codesign(mecab_bundle, hardened_runtime=False, force=True, mecab=True)
            logger.info('✅ Finished signing mecab bundle')

    def sign_sasl_plugins(self):
        """ Actually signs libdigestmd5.plugin
        """
        if (md5_plugin := self.config.path_to_app_bundle / 'Contents/SASL Plugins/libdigestmd5.plugin').exists():
            logger.info('Signing 4D md5 plugin ...')
            self.codesign(md5_plugin, hardened_runtime=False, force=True)
            logger.info('✅ Finished signing 4D md5 plugin')

    def sign_contents(self):
        """ Signs files(!) one level below the 'Contents' directory with some exceptions.
        """
        excluded_names: list[str] = ['PkgInfo', 'CodeResources', 'Info.plist']

        if (contents_dir := self.config.path_to_app_bundle / 'Contents').exists():
            logger.info('Signing "Contents" directory ...')

            for item in contents_dir.glob('*'):
                if item.is_file() and item.name not in excluded_names:
                    self.codesign(item, hardened_runtime=False, force=True)

            logger.info('✅ Finished signing "Contents" directory')

    def remove_php(self):
        """ Removes php for macOS
        """
        php_dir: Path = self.config.path_to_app_bundle / 'Contents/Resources/php/Mac'
        shutil.rmtree(php_dir)
        logger.info('Removed PHP for macOS at "%s"', php_dir)

    def sign_php(self):
        """ Signs php for macOS """
        if (php := self.config.path_to_app_bundle / 'Contents/Resources/php/Mac/php-fcgi-4d').exists():
            self.codesign(php, hardened_runtime=True, force=True)
            logger.info('✅ Finished signing PHP for macOS')

    def sign_bin_dir(self):
        """ Signs recursively a (presumably optional) 'bin' directory
        """
        if (internal_components := self.config.path_to_app_bundle / 'Contents/Resources/bin').exists():
            logger.info('Signing bin directory ...')

            for item in internal_components.rglob('*'):
                if not item.name.startswith('.'):
                    self.codesign(item, hardened_runtime=True, force=True)

            logger.info('✅ Finished signing bin directory')

    def sign_app(self):
        """ Signs the main application bundle (self.path_to_app_bundle).
        """
        logger.info('Signing main application bundle "%s" ...', self.config.path_to_app_bundle.name)
        self.codesign(item_to_sign=self.config.path_to_app_bundle, hardened_runtime=True)
        logger.info('✅ Finished signing main application bundle "%s"',
                    self.config.path_to_app_bundle.name)

    def codesign(self, item_to_sign: Path, hardened_runtime: bool, **options):
        """ Main entry point to sign a file or bundle.

        :param item_to_sign: The file or bundle which is about to be signed
        :param hardened_runtime: True if the item must be hardened for runtime
        :param options: optional dictionary with signing-options. Constraints are
            'mecab' (bool), 'local' (bool), 'force' (bool)
        """
        # TODO: unit tests

        if item_to_sign.is_dir():
            info_plist_name: Final[str] = 'Info.plist'
            info_plist_file: Path

            bundle_type: str = item_to_sign.suffix
            info_plist_file = item_to_sign / 'Contents' / info_plist_name

            if not info_plist_file.exists():
                # Look for plist in .framework and resolve possible symlinks
                resources_dir = (item_to_sign / 'Resources').resolve()
                info_plist_file = resources_dir / info_plist_name

            if not info_plist_file.exists():
                raise FileNotFoundError(
                    'Unable to find "%s" for item "%s"' % (info_plist_name, item_to_sign))

            if options.get('mecab'):
                self.lowercase_executable_name(path_to_plist=info_plist_file)

            if bundle_type == '.app':
                self.update_info_plist(path_to_plist=info_plist_file,
                                       custom_keys=self.config.plist_data)

        additional_codesign_command_args: list = []

        if not options.get('local'):
            additional_codesign_command_args.append('--timestamp')

        if options.get('force'):
            additional_codesign_command_args.append('--force')

        if hardened_runtime:
            path_to_temp_plist: Path = \
                codesigning.create_entitlements_plist(
                    self.config.default_hardened_runtime_entitlements)

            try:
                codesigning.run_codesign_command_for_hardened_runtime(
                    path_to_plist=path_to_temp_plist,
                    path_to_item=item_to_sign,
                    identity=self.config.signing_identity,
                    args=additional_codesign_command_args)

            finally:
                # Always remove the temporary dir created by codesigning.create_entitlements_plist()
                shutil.rmtree(path_to_temp_plist.parent, ignore_errors=True)

        else:
            codesigning.run_codesign_command(path_to_item=item_to_sign,
                                             identity=self.config.signing_identity,
                                             args=additional_codesign_command_args)

    def lowercase_executable_name(self, path_to_plist: Path):
        """ Changes bundle executable name to lowercase in plist file

        :param path_to_plist: Path to the Info.plist
        """
        if not path_to_plist.exists():
            raise FileNotFoundError('%s does not exist' % path_to_plist)

        # Read and pre-parse file
        logger.debug('Parsing %s', path_to_plist)
        plist: etree_ElementTree = etree.parse(str(path_to_plist))
        top_element: etree_Element = plist.getroot().find('dict')

        element: etree_Element = top_element.find("key[.='CFBundleExecutable']")
        if not element.text: return

        # The next-sibling element is <string>YourBundleExecutableName</string>
        next_sibling: etree_Element = element.getnext()
        executable_name: str = next_sibling.text
        if not executable_name: return

        # Finally... change to lowercase
        next_sibling.text = executable_name.lower()

        # Write changes to file
        plist.write(str(path_to_plist), encoding="utf-8")
        codesigning.convert_to_plist_format(path_to_plist)
        # Modification to *.plist invalidates the signature -- re-sign
        codesigning.run_codesign_command(path_to_item=path_to_plist,
                                         identity=self.config.signing_identity)

        logger.info('Changed bundle executable name: "%s" --> "%s"',
                    executable_name, executable_name.lower())

    def update_info_plist(self, path_to_plist: Path, custom_keys: dict = None):
        """ Modifies the given Info.plist file by passing custom_keys or default keys.

        :param path_to_plist: Path to the Info.plist
        :param custom_keys: optional; custom_keys dict if passed, else we're using
            fixed default keys from default_info_plist_properties.
        """
        if not path_to_plist.exists():
            raise FileNotFoundError('%s does not exist' % path_to_plist)

        logger.info('Updating properties of plist at "%s"', path_to_plist)

        # Take custom_keys if passed, else take fixed default keys
        given_keys: dict = custom_keys if custom_keys else self.config.default_info_plist_properties

        # Read and pre-parse file
        logger.debug('Parsing %s', path_to_plist)
        plist: etree_ElementTree = etree.parse(str(path_to_plist))
        top_element: etree_Element = plist.getroot().find('dict')

        # 1) Remove keys/values which we want to write, but already exist in Info.plist

        for given_key in given_keys:
            found_elements: list[etree_Element] = top_element.xpath(f'.//key[text()="{given_key}"]')

            if found_elements:
                this_element_text: str = found_elements[0].text
                next_sibling: etree_Element = found_elements[0].getnext()
                next_sibling_info: str = next_sibling.text

                logger.debug('Removing value "%s" for <key> "%s" from %s',
                             next_sibling_info,
                             this_element_text,
                             path_to_plist.name)

                top_element.remove(next_sibling)

                logger.debug('Removing <key> from %s: "%s"',
                             path_to_plist.name,
                             this_element_text)

                top_element.remove(found_elements[0])

        # 2) Write keys/values

        for given_key, given_value in given_keys.items():
            element: etree_Element = etree.Element('key')
            element.text = given_key
            top_element.append(element)
            logger.debug('Appended <key> to %s: "%s"', path_to_plist.name, element.text)

            if isinstance(given_value, str):
                element: etree_Element = etree.Element('string')
                element.text = given_value
                top_element.append(element)
                logger.debug('Appended <string> to %s: "%s"', path_to_plist.name, element.text)

            elif isinstance(given_value, bool):
                element: etree_Element = etree.Element('true' if given_value else 'false')
                top_element.append(element)
                logger.debug('Appended boolean to %s: "%s"', path_to_plist.name, element.text)

            elif isinstance(given_value, list):
                array: etree_Element = etree.Element('array')
                for keyValue in given_value:
                    element = etree.Element('string')
                    element.text = keyValue
                    array.append(element)
                    logger.debug('Appended <string> to array of %s: "%s"', path_to_plist.name,
                                 element.text)
                top_element.append(array)

        # Write changes to file
        plist.write(str(path_to_plist), encoding="utf-8")
        codesigning.convert_to_plist_format(path_to_plist)
        # Modification to *.plist invalidates the signature -- re-sign
        codesigning.run_codesign_command(path_to_item=path_to_plist,
                                         identity=self.config.signing_identity)

        logger.info('✅ Finished updating properties of plist at "%s"', path_to_plist)
