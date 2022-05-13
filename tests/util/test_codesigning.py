import shutil
import subprocess
import unittest
from pathlib import Path
from unittest import TestCase

from core import IS_WINDOWS
from core.codesign_config import CodesignConfig
from testhelper import create_app_template_file_copy, create_temp_testing_dir, PATH_TO_4D_TEMPLATE_APP, \
    MESSAGE_SKIPPED_CAUSED_BY_TEMPLATE, DEVELOPER_ID_APPLICATION_ENTRY
from util import codesigning, processes
from util.logging import set_root_loglevel


@unittest.skipIf(IS_WINDOWS, 'Not applicable for Windows')
class TestCodesigning(TestCase):
    """ Test codesigning utilities """

    @classmethod
    def setUpClass(cls) -> None:
        set_root_loglevel(name='INFO')

    def setUp(self) -> None:
        # Cleanup the 'temp' testing-directory and create a new one.
        create_temp_testing_dir()

    def tearDown(self) -> None:
        pass
        # Note: We do not remove the 'temp' directory at tearDown - for manual inspection purposes.
        # It gets removed/created within the setUp phase.

    def test_run_codesign_command__signsAsExpectedIfPassedValidArguments(self):
        # Note that a valid "Developer ID Application: ..." Certificate must be installed to succeed.

        # given
        # Keep our test fixture save - create a copy for tests.
        # - Mission Control.app is a small Apple application
        # - Signed Mission Control.app is our temporary working copy which gets modified by tests.
        template_item_to_sign: Path = Path('tests/resources/fixtures/Mission Control.app')
        testing_item_to_sign: Path = Path('tests/resources/temp/Signed Mission Control.app')
        shutil.copytree(template_item_to_sign, testing_item_to_sign, dirs_exist_ok=True)

        # when
        result = codesigning.run_codesign_command(path_to_item=testing_item_to_sign,
                                                  identity=DEVELOPER_ID_APPLICATION_ENTRY,
                                                  args=['--force'])

        # then
        self.assertEqual(result.returncode, 0)
        self.assertIn('signed', result.stdout)
        self.assertIn(testing_item_to_sign.name, result.stdout)
        self.assertHasValidSigning(testing_item_to_sign)

    def test_run_codesign_command__raisesWithStderrIfSomethingWentWrong(self):
        # given
        file_to_sign: Path = Path('I do not exist.png')

        with self.assertRaises(subprocess.SubprocessError):
            # when
            result = codesigning.run_codesign_command(path_to_item=file_to_sign,
                                                      identity=DEVELOPER_ID_APPLICATION_ENTRY)

            # then
            self.assertEqual(result.returncode, 1)
            self.assertIn('No such file or directory', result.stdout)
            self.assertIn(file_to_sign.name, result.stdout)

    def test_create_entitlements_plist_createsFileAsExpectedWithDefaultEntitlements(self):
        # Note that a valid "Developer ID Application: ..." Certificate must be installed to succeed.

        # given
        config: CodesignConfig = CodesignConfig(path_to_app_bundle=Path('StubbedPath'),
                                                signing_identity=DEVELOPER_ID_APPLICATION_ENTRY,
                                                plist_data=None)

        default_entitlements: dict = config.default_info_plist_properties

        # when
        temp_entitlements_plist: Path = codesigning.create_entitlements_plist(entitlements=default_entitlements)

        # then
        self.assertTrue(temp_entitlements_plist.exists(),
                        'Expected existing temporary file "entitlements.plist", but it does not exist.')

        # Remove temporary dir created by create_entitlements_plist()
        shutil.rmtree(temp_entitlements_plist.parent, ignore_errors=True)

    def test_remove_extended_attributes__recursivelyRemovesAllExtendedAttributes(self):
        bundle_stub: Path = Path('tests/resources/temp/Test.app')

        # Just an inner helper function to read extended attributes from a bundle
        def get_attributes() -> list:
            cmd: list = ['xattr', '-lr', bundle_stub]
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            return result.stdout.strip().splitlines()

        # given

        # Clean up before, just in case...
        shutil.rmtree(bundle_stub, ignore_errors=True)

        # And create a bundle tree stub for tests with root Test.app
        bundle_stub.mkdir()
        (bundle_stub / 'A/B').mkdir(parents=True)
        (bundle_stub / 'Just a test.sh').touch()
        (bundle_stub / 'Just another test.sh').touch()
        (bundle_stub / 'A/B/Some nested file.sh').touch()

        # Recursively set an attribute
        command: list = ['xattr', '-w', '-r', 'MyTestAttrName', 'MyTestAttrValue', bundle_stub]
        subprocess.run(command)
        # Check if it was set, as we need that setup for the main test.
        attributes_before: list = get_attributes()
        assert any('MyTestAttrName: MyTestAttrValue' in string for string in attributes_before)
        assert len(attributes_before) == 6  # each item in our test bundle tree

        # when
        codesigning.remove_extended_attributes(path_to_item=bundle_stub)

        # then
        attributes_after: list = get_attributes()
        self.assertListEqual(attributes_after, [])  # should be empty now

    def assertHasValidSigning(self, path_to_item: Path):
        """ Can be called to assert a valid signature.

        :param path_to_item: Path to the file or bundle whose signature should be verified locally.
        """
        if not path_to_item.exists(): return

        verification_result = processes.run_subprocess(
            ['codesign', '--verify', '--deep', '--verbose', path_to_item])
        self.assertEqual(verification_result.returncode, 0)
        self.assertIn('valid on disk', verification_result.stdout)
        self.assertIn('satisfies its Designated Requirement', verification_result.stdout)

    def test_run_install_name_tool__raisesIfFileOrDirectoryNotExists(self):
        # given
        source: Path = Path('tests/resources/fixtures/Mission Control.app')
        _from: str = '@executable_path/../Frameworks/Chromium Embedded Framework.framework/Chromium Embedded Framework'
        _to: str = '@executable_path/../../../../Frameworks/Chromium Embedded Framework.framework/' \
                   'Chromium Embedded Framework'

        # when
        with self.assertRaises(subprocess.SubprocessError) as context:
            codesigning.run_install_name_tool(source=source, _from=_from, _to=_to)

            # then
            self.assertIn("can't open file", str(context.exception))

    @unittest.skipIf(not PATH_TO_4D_TEMPLATE_APP.exists(), MESSAGE_SKIPPED_CAUSED_BY_TEMPLATE)
    def test_run_install_name_tool__succeedsIfGivenPathsAndFrameworksExist(self):
        # Note that a valid "Developer ID Application: ..." Certificate must be installed to succeed.

        # given

        path_to_app_bundle: Path = create_app_template_file_copy()
        assert path_to_app_bundle.exists()

        source: Path = \
            path_to_app_bundle / 'Contents/Native Components/WebViewerCEF.bundle/Contents/Frameworks/' \
                                 '4D Helper.app/Contents/MacOS/4D Helper'
        _from: str = '@executable_path/../Frameworks/Chromium Embedded Framework.framework/Chromium Embedded Framework'
        _to: str = '@executable_path/../../../../Frameworks/Chromium Embedded Framework.framework/' \
                   'Chromium Embedded Framework'

        # when
        result = codesigning.run_install_name_tool(source=source, _from=_from, _to=_to)

        # then
        self.assertEqual(0, result.returncode)

        # cleanup
        shutil.rmtree(path_to_app_bundle, ignore_errors=True)
