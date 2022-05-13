""" This module provides several helpers for frequently used test-objects.
"""

import shutil
from pathlib import Path
from typing import Final

from util import processes

PATH_TO_4D_TEMPLATE_APP: Final[Path] = Path('tests/resources/fixtures/4D-template-complete.app')
""" This .app file may be large, thus not versioned. Simply copy your 4D app bundle to this path
and rename it to this filename to run tests on it.  """

MESSAGE_SKIPPED_CAUSED_BY_TEMPLATE: Final[str] = \
    'To run this test, create a complete valid 4D-template-complete.app at the expected location ' \
    f'(it must be located at {PATH_TO_4D_TEMPLATE_APP})'

# IMPORTANT
# Replace this string with your codesigning identity string as stored in your macOS keychain.
# Otherwise, related tests will fail:
DEVELOPER_ID_APPLICATION_ENTRY: Final[str] = 'Developer ID Application: Fantastic Software AG (1XY2345678)'


def create_temp_testing_dir() -> Path:
    """ Removes testing-directory 'tests/resources/temp' and creates a new one.

    :return: Path to the empty temporary testing-directory
    """
    path_to_temp_dir: Path = Path('tests/resources/temp').resolve()

    shutil.rmtree(path_to_temp_dir, ignore_errors=True)
    path_to_temp_dir.mkdir()

    return path_to_temp_dir


def create_app_template_file_copy() -> Path:
    """ Keeps our test fixture save - creates a copy for tests and deeply removes its signature.

    :return: Path to the working copy of the app
    """
    destination: Path = create_temp_testing_dir() / PATH_TO_4D_TEMPLATE_APP.name
    shutil.copytree(src=PATH_TO_4D_TEMPLATE_APP, dst=destination, dirs_exist_ok=True, symlinks=True)
    remove_signing(path_to_item=destination)

    return destination


def remove_signing(path_to_item: Path):
    """ This is a test helper - removes signature before doing any signing-tests.

    :param path_to_item: Path to the file or bundle whose signature should be removed
    """
    processes.run_subprocess(commands=['codesign', '--deep', '--remove-signature', path_to_item])
