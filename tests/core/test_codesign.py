import shutil
import subprocess
import unittest
from pathlib import Path
from unittest import TestCase

from lxml import etree
# noinspection PyProtectedMember
from lxml.etree import _Element as etree_Element
# noinspection PyProtectedMember
from lxml.etree import _ElementTree as etree_ElementTree

from core import IS_WINDOWS
from core.codesign import Codesign
from core.codesign_config import CodesignConfig
from testhelper import create_temp_testing_dir, PATH_TO_4D_TEMPLATE_APP, MESSAGE_SKIPPED_CAUSED_BY_TEMPLATE, \
    create_app_template_file_copy, remove_signing, DEVELOPER_ID_APPLICATION_ENTRY
from util import processes
from util.logging import set_root_loglevel


@unittest.skipIf(IS_WINDOWS, 'Not applicable for Windows')
class TestCodesign(TestCase):
    """ Unit tests for class Codesign """

    @classmethod
    def setUpClass(cls) -> None:
        set_root_loglevel(name='INFO')

    def setUp(self) -> None:
        # Cleanup the 'temp' testing-directory and create a new one.
        temp_dir: Path = create_temp_testing_dir()

        # Create stub of an .app bundle
        path_to_bundle_stub = Path(temp_dir / 'Test.app')
        # Clean up before, just in case...
        shutil.rmtree(path_to_bundle_stub, ignore_errors=True)

        # And create a bundle tree stub for tests with root Test.app
        path_to_bundle_stub.mkdir()
        (path_to_bundle_stub / 'A/B').mkdir(parents=True)
        (path_to_bundle_stub / 'B').mkdir()

        self.codesign_config: CodesignConfig = \
            CodesignConfig(path_to_bundle_stub, signing_identity=DEVELOPER_ID_APPLICATION_ENTRY, plist_data=None)

        # Create the instance under test
        self.codesign: Codesign = Codesign(config=self.codesign_config)

    def tearDown(self) -> None:
        # Cleanup
        del self.codesign, self.codesign_config
        # Note: We do not remove the 'temp' directory at tearDown - for manual inspection purposes.
        # It gets removed/created within the setUp phase.

    @unittest.skipIf(not PATH_TO_4D_TEMPLATE_APP.exists(), MESSAGE_SKIPPED_CAUSED_BY_TEMPLATE)
    def test_run__succeedsIfEnvironmentHasValidSetup(self):
        # Note that a valid "Developer ID Application: ..." Certificate must be installed to succeed.

        # given
        self.codesign.config.path_to_app_bundle = create_app_template_file_copy()

        # when
        self.codesign.run()

        # then
        self.assertHasValidSigning(path_to_item=self.codesign.config.path_to_app_bundle)

    @unittest.skipIf(not PATH_TO_4D_TEMPLATE_APP.exists(), MESSAGE_SKIPPED_CAUSED_BY_TEMPLATE)
    def test_sign_app__succeedsIfEnvironmentHasValidSetup(self):
        # Note that a valid "Developer ID Application: ..." Certificate must be installed to succeed.

        # given
        self.codesign.config.path_to_app_bundle = create_app_template_file_copy()

        # when
        self.codesign.sign_app()

        # then
        self.assertHasValidSigning(self.codesign.config.path_to_app_bundle)

    @unittest.skipIf(not PATH_TO_4D_TEMPLATE_APP.exists(), MESSAGE_SKIPPED_CAUSED_BY_TEMPLATE)
    def test_pre_cleanup__removesSignaturesAsExpected(self):
        # Note that a valid "Developer ID Application: ..." Certificate must be installed to succeed.

        # given
        self.codesign.config.path_to_app_bundle = create_app_template_file_copy()
        app_bundle = self.codesign.config.path_to_app_bundle

        # when
        self.codesign.pre_cleanup()

        # then
        # 1) Expect main application bundle being unsigned
        self.assertIsUnsigned(app_bundle)

        # 2) Expect top-level items of 'Native Components' directory being unsigned
        if self.codesign.config.runner_options.get('signNativeComponents'):
            native_components: Path = app_bundle / 'Contents/Native Components'
            [self.assertIsUnsigned(component) for component in native_components.glob('*')]

    @unittest.skipIf(not PATH_TO_4D_TEMPLATE_APP.exists(), MESSAGE_SKIPPED_CAUSED_BY_TEMPLATE)
    def test_sign_helpers__succeedsIfEnvironmentHasValidSetup(self):
        # Note that a valid "Developer ID Application: ..." Certificate must be installed to succeed.

        # given
        self.codesign.path_to_app_bundle = create_app_template_file_copy()

        # when
        self.codesign.sign_helpers()

        # then
        app = self.codesign.path_to_app_bundle
        self.assertHasValidSigning(app / 'Contents/MacOS/HelperTool')
        self.assertHasValidSigning(app / 'Contents/MacOS/InstallTool')
        self.assertHasValidSigning(app / 'Contents/MacOS/InstallTool.app/Contents/Library/LaunchServices/com.4D.Helper')
        self.assertHasValidSigning(app / 'Contents/MacOS/InstallTool.app')

    @unittest.skipIf(not PATH_TO_4D_TEMPLATE_APP.exists(), MESSAGE_SKIPPED_CAUSED_BY_TEMPLATE)
    def test_sign_native_components__succeedsIfEnvironmentHasValidSetup(self):
        # Note that a valid "Developer ID Application: ..." Certificate must be installed to succeed.

        # given

        self.codesign.config.path_to_app_bundle = create_app_template_file_copy()
        # Remove signing first, else we get an 'already signed' error for each *bundle
        app: Path = self.codesign.config.path_to_app_bundle
        native_components: Path = app / 'Contents/Native Components'
        for component_bundle in native_components.glob('*'):
            remove_signing(component_bundle)

        # when
        self.codesign.sign_native_components()

        # then
        # Assert that each top-level bundle of dir 'Native Components' got a valid signature
        for item in (app / 'Contents/Native Components/WebViewerCEF.bundle/Contents/Frameworks').glob('*'):
            self.assertHasValidSigning(item)

    @unittest.skipIf(not PATH_TO_4D_TEMPLATE_APP.exists(), MESSAGE_SKIPPED_CAUSED_BY_TEMPLATE)
    def test_sign_updater__succeedsIfEnvironmentHasValidSetup(self):
        # Note that a valid "Developer ID Application: ..." Certificate must be installed to succeed.

        # given
        self.codesign.path_to_app_bundle = create_app_template_file_copy()

        # when
        self.codesign.sign_updater()

        # then
        app = self.codesign.path_to_app_bundle

        self.assertHasValidSigning(app / 'Contents/Resources/Updater/Updater.app')

        updater_frameworks = app / 'Contents/Resources/Updater/Updater.app/Contents/Frameworks'
        for item in updater_frameworks.rglob('*'):
            if not item.name.startswith('.'):
                self.assertHasValidSigning(item)

    @unittest.skipIf(not PATH_TO_4D_TEMPLATE_APP.exists(), MESSAGE_SKIPPED_CAUSED_BY_TEMPLATE)
    def test_sign_frameworks__succeedsIfEnvironmentHasValidSetup(self):
        # Note that a valid "Developer ID Application: ..." Certificate must be installed to succeed.

        # given
        self.codesign.path_to_app_bundle = create_app_template_file_copy()

        # when
        self.codesign.sign_frameworks()

        # then
        if (frameworks := self.codesign.path_to_app_bundle / 'Contents/Frameworks').exists():
            for item in frameworks.glob('*'):
                self.assertHasValidSigning(item)

    @unittest.skipIf(not PATH_TO_4D_TEMPLATE_APP.exists(), MESSAGE_SKIPPED_CAUSED_BY_TEMPLATE)
    def test_sign_internal_components__succeedsIfEnvironmentHasValidSetup(self):
        # Note that a valid "Developer ID Application: ..." Certificate must be installed to succeed.

        # given
        path_fragment = Path('Contents/Resources/Internal Components')

        if not (PATH_TO_4D_TEMPLATE_APP / path_fragment).exists():
            self.skipTest('"Internal Components" directory does not exist in .app bundle, cannot test')

        self.codesign.config.path_to_app_bundle = create_app_template_file_copy()
        internal_components: Path = self.codesign.config.path_to_app_bundle / path_fragment
        accepted_suffixes = [".html", ".json", ".js", ".dylib"]

        # when
        self.codesign.sign_internal_components()

        # then
        for item in internal_components.rglob('*'):
            if not item.name.startswith('.') and item.suffix in accepted_suffixes:
                self.assertHasValidSigning(item)

    @unittest.skipIf(not PATH_TO_4D_TEMPLATE_APP.exists(), MESSAGE_SKIPPED_CAUSED_BY_TEMPLATE)
    def test_sign_plugins__succeedsIfEnvironmentHasValidSetup(self):
        # Note that a valid "Developer ID Application: ..." Certificate must be installed to succeed.

        # given
        path_fragment = 'Contents/Plugins'

        if not (PATH_TO_4D_TEMPLATE_APP / path_fragment).exists():
            self.skipTest('"Plugins" directory does not exist in .app bundle, cannot test')

        self.codesign.path_to_app_bundle = create_app_template_file_copy()
        plugins_dir: Path = self.codesign.path_to_app_bundle / path_fragment

        # when
        self.codesign.sign_plugins()

        # then
        for plugin in plugins_dir.glob('*.bundle'):
            self.assertHasValidSigning(plugin)

    @unittest.skipIf(not PATH_TO_4D_TEMPLATE_APP.exists(), MESSAGE_SKIPPED_CAUSED_BY_TEMPLATE)
    def test_sign_components__succeedsIfEnvironmentHasValidSetup(self):
        # Note that a valid "Developer ID Application: ..." Certificate must be installed to succeed.

        # given
        path_fragment = Path('Contents/Components')

        if not (PATH_TO_4D_TEMPLATE_APP / path_fragment).exists():
            self.skipTest('"Components" directory does not exist in .app bundle, cannot test')

        self.codesign.config.path_to_app_bundle = create_app_template_file_copy()
        components: Path = self.codesign.config.path_to_app_bundle / path_fragment
        accepted_suffixes = [".html", ".json", ".js", ".dylib"]

        # when
        self.codesign.sign_components()

        # then
        for item in components.rglob('*'):
            if not item.name.startswith('.') and item.suffix in accepted_suffixes:
                self.assertHasValidSigning(item)

    @unittest.skipIf(not PATH_TO_4D_TEMPLATE_APP.exists(), MESSAGE_SKIPPED_CAUSED_BY_TEMPLATE)
    def test_sign_database__succeedsIfEnvironmentHasValidSetup(self):
        # Note that a valid "Developer ID Application: ..." Certificate must be installed to succeed.

        # given
        path_fragment = Path('Contents/Database')  # Standalone *.app

        if not (PATH_TO_4D_TEMPLATE_APP / path_fragment).exists():
            self.skipTest('"Database" directory does not exist in .app bundle, cannot test')

        self.codesign.config.path_to_app_bundle = create_app_template_file_copy()
        database_dir: Path = self.codesign.config.path_to_app_bundle / path_fragment
        accepted_suffixes = [".html", ".json", ".js", ".dylib"]

        # when
        self.codesign.sign_database(suffixes=accepted_suffixes)

        # then
        for item in database_dir.rglob('*'):
            if not item.name.startswith('.') and item.suffix in accepted_suffixes:
                self.assertHasValidSigning(item)

    @unittest.skipIf(not PATH_TO_4D_TEMPLATE_APP.exists(), MESSAGE_SKIPPED_CAUSED_BY_TEMPLATE)
    def test_sign_mecab__succeedsIfEnvironmentHasValidSetup(self):
        # given
        path_fragment = 'Contents/Resources/mecab/mecab.bundle'

        mecab: Path = PATH_TO_4D_TEMPLATE_APP / path_fragment
        if not (PATH_TO_4D_TEMPLATE_APP / path_fragment).exists():
            self.skipTest(f'Bundle "{mecab.name}" does not exist, cannot test')

        self.codesign.path_to_app_bundle = create_app_template_file_copy()
        mecab = self.codesign.path_to_app_bundle / path_fragment

        # when
        self.codesign.sign_mecab()

        # then
        self.assertHasValidSigning(mecab)

    @unittest.skipIf(not PATH_TO_4D_TEMPLATE_APP.exists(), MESSAGE_SKIPPED_CAUSED_BY_TEMPLATE)
    def test_sign_sasl_plugins__succeedsIfEnvironmentHasValidSetup(self):
        # given
        path_fragment = 'Contents/SASL Plugins/libdigestmd5.plugin'

        md5_plugin: Path = PATH_TO_4D_TEMPLATE_APP / path_fragment
        if not (PATH_TO_4D_TEMPLATE_APP / path_fragment).exists():
            self.skipTest(f'File "{md5_plugin.name}" does not exist in .app bundle, cannot test')

        self.codesign.path_to_app_bundle = create_app_template_file_copy()
        md5_plugin = self.codesign.path_to_app_bundle / path_fragment

        # when
        self.codesign.sign_sasl_plugins()

        # then
        self.assertHasValidSigning(md5_plugin)

    @unittest.skipIf(not PATH_TO_4D_TEMPLATE_APP.exists(), MESSAGE_SKIPPED_CAUSED_BY_TEMPLATE)
    def test_sign_contents__succeedsIfEnvironmentHasValidSetup(self):
        # Note that a valid "Developer ID Application: ..." Certificate must be installed to succeed.

        # given
        path_fragment = Path('Contents')

        if not (PATH_TO_4D_TEMPLATE_APP / path_fragment).exists():
            self.skipTest('"Contents" directory does not exist in .app bundle, cannot test')

        self.codesign.path_to_app_bundle = create_app_template_file_copy()
        contents_dir: Path = self.codesign.path_to_app_bundle / path_fragment
        excluded_names: list[str] = ['PkgInfo', 'CodeResources', 'Info.plist']

        # when
        self.codesign.sign_contents()

        # then
        for item in contents_dir.glob('*'):
            if item.is_file() and item.name not in excluded_names:
                self.assertHasValidSigning(item)

    @unittest.skipIf(not PATH_TO_4D_TEMPLATE_APP.exists(), MESSAGE_SKIPPED_CAUSED_BY_TEMPLATE)
    def test_sign_php__succeedsIfEnvironmentHasValidSetup(self):
        # given
        path_fragment = 'Contents/Resources/php/Mac/php-fcgi-4d'

        php: Path = PATH_TO_4D_TEMPLATE_APP / path_fragment
        if not (PATH_TO_4D_TEMPLATE_APP / path_fragment).exists():
            self.skipTest(f'File "{php.name}" does not exist in .app bundle, cannot test')

        self.codesign.path_to_app_bundle = create_app_template_file_copy()
        php: Path = self.codesign.path_to_app_bundle / path_fragment

        # when
        self.codesign.sign_php()

        # then
        self.assertHasValidSigning(php)

    @unittest.skipIf(not PATH_TO_4D_TEMPLATE_APP.exists(), MESSAGE_SKIPPED_CAUSED_BY_TEMPLATE)
    def test_sign_bin_dir__succeedsIfEnvironmentHasValidSetup(self):
        # Note that a valid "Developer ID Application: ..." Certificate must be installed to succeed.

        # given
        path_fragment = 'Contents/Resources/bin'

        if not (PATH_TO_4D_TEMPLATE_APP / path_fragment).exists():
            self.skipTest('"bin" directory does not exist in .app bundle, cannot test')

        self.codesign.path_to_app_bundle = create_app_template_file_copy()
        bin_directory: Path = self.codesign.path_to_app_bundle / path_fragment

        # when
        self.codesign.sign_bin_dir()

        # then
        for item in bin_directory.rglob('*'):
            if not item.name.startswith('.'):
                self.assertHasValidSigning(item)

    @unittest.skipIf(not PATH_TO_4D_TEMPLATE_APP.exists(), MESSAGE_SKIPPED_CAUSED_BY_TEMPLATE)
    def test_remove_php__removesPhpDirectoryForMacIfPresent(self):
        # given
        path_fragment = 'Contents/Resources/php/Mac'

        if not (PATH_TO_4D_TEMPLATE_APP / path_fragment).exists():
            self.skipTest('php directory does not exist in .app bundle, cannot test')

        self.codesign.config.path_to_app_bundle = create_app_template_file_copy()
        php_dir: Path = self.codesign.config.path_to_app_bundle / path_fragment

        # when
        self.codesign.remove_php()

        # then
        self.assertFalse(php_dir.exists(), 'Expected non existing PHP directory, but it still exists')

    def test_remove_temp_files__deletesAllSpecifiedFilesRecursively(self):
        # given
        bundle: Path = self.codesign.config.path_to_app_bundle
        # Create a tree with some '.cstemp' files in it
        (bundle / 'Just a test.cstemp').touch()  # 1
        (bundle / 'A/One more test.cstemp').touch()  # 2
        (bundle / 'A/B/4D is evil.cstemp').touch()  # 3
        (bundle / 'B/Take care.cstemp').touch()  # 4

        # Check if test environment has been created
        assert len(list(bundle.rglob('*.cstemp'))) == 4

        # when
        self.codesign.remove_temp_files()

        # then
        # Assert that there are no files with extension '.cstemp' anymore
        self.assertEqual(list(bundle.rglob('*.cstemp')), [])

    def test_remove_component_plugins__shouldRemoveAllPluginFoldersOneLevelBelowEachComponent(self):
        # given
        # Create a tree
        components_dir = (self.codesign.config.path_to_app_bundle / 'Contents/Components')
        components_dir.mkdir(parents=True)

        (components_dir / 'SomeHolyComponent.4dbase/Plugins').mkdir(parents=True)  # 1
        (components_dir / 'SomeOtherComponent.4dbase/Plugins').mkdir(parents=True)  # 2

        # Check if test environment has been created
        assert len(list(components_dir.glob('*/Plugins'))) == 2

        # when
        self.codesign.remove_component_plugins()

        # then
        # Assert that there are no 'Plugin' dirs one level below each component anymore
        self.assertEqual(list(components_dir.glob('*/Plugins')), [])

    def test_update_info_plist__updatesElementsAsExpected(self):
        # Note that a valid "Developer ID Application: ..." Certificate must be installed to succeed.

        # given

        # Keep our test fixture save - create a copy for tests.
        # - 4DTest_Info.plist is a valid build artifact of a 4D Build.
        # - Modified_Info.plist is our temporary working copy which gets modified by tests.
        template_info_plist_file = Path('tests/resources/fixtures/4DTest_Info.plist')
        testing_info_plist_file = Path('tests/resources/temp/Modified_Info.plist')

        expected_properties: dict = {
            'NSRequiresAquaSystemAppearance': 'Test some AquaSystemAppearance',
            'NSAppleEventsUsageDescription': 'Test some AppleEvents description',
            'NSCalendarsUsageDescription': 'Test some Calendars description',
            'NSContactsUsageDescription': 'Test some Contacts description',
            'NSRemindersUsageDescription': 'Test some Reminders description',
            'NSCameraUsageDescription': 'Test some Camera description',
            'NSMicrophoneUsageDescription': 'Test some Microphone description',
            'NSLocationUsageDescription': 'Test some Location description',
            'NSPhotoLibraryUsageDescription': 'Test some PhotoLibrary description',
            'NSSystemAdministrationUsageDescription': 'Test some SystemAdministration description',
            'ThisKeyDoesNotExistInTemplateExpectToBeAdded': 'Test some additional entry',
            'ThisBooleanDoesNotExistInTemplateExpectToBeAddedAndSetToTrue': True,
            'ThisBooleanDoesNotExistInTemplateExpectToBeAddedAndSetToFalse': False,
            'ThisArrayDoesNotExistExpectInTemplateExpectToBeAdded': [
                'Test some array 1',
                'Test some array 2',
                'Test some array 3'
            ]
        }

        # when
        subtest_names = ['with custom properties', 'without custom properties']
        for subtest_name in subtest_names:

            # Cleanup & copy for temporary file
            testing_info_plist_file.unlink(missing_ok=True)  # cleanup
            shutil.copy(template_info_plist_file, testing_info_plist_file)

            # Run each subtest
            with self.subTest(subtest=subtest_name):
                if subtest_name == 'with custom properties':
                    # Use and pass the expected_properties defined above as the 2nd parameter.
                    # Also use it for later comparison.
                    self.codesign.update_info_plist(testing_info_plist_file, expected_properties)
                else:
                    # Call without 2nd parameter.
                    # Use default data for later comparison.
                    expected_properties = self.codesign.config.default_info_plist_properties
                    self.codesign.update_info_plist(testing_info_plist_file)

                # Prepare test results: Create a comparable "resulting_properties"
                # dictionary by re-parsing the modified test file
                plist: etree_ElementTree = etree.parse(str(testing_info_plist_file))
                top_element: etree_Element = plist.getroot().find('dict')
                resulting_properties: dict = {}

                for element in top_element:
                    element: etree_Element  # for IDE's type-ahead

                    if element.text in expected_properties.keys():
                        next_sibling: etree_Element = element.getnext()

                        if next_sibling.tag == 'true':
                            resulting_properties.update({element.text: True})

                        if next_sibling.tag == 'false':
                            resulting_properties.update({element.text: False})

                        elif next_sibling.tag == 'string':
                            next_next_sibling_text = element.getnext().text
                            next_next_sibling_text = '' if next_next_sibling_text is None else next_next_sibling_text
                            resulting_properties.update({element.text: next_next_sibling_text})

                        elif next_sibling.tag == 'array':
                            values = []
                            for array_element in next_sibling:
                                values.append(array_element.text)
                            resulting_properties.update({element.text: values})

                # then
                # Expect both data dictionaries to be equal
                self.assertListEqual(sorted(expected_properties.items()), sorted(resulting_properties.items()))

        # Note: We do not remove the modified file - for manual inspection purposes.

    def test_lowercase_executable_name__setsBundleNameToLowercaseInPlistFile(self):
        # Note that a valid "Developer ID Application: ..." Certificate must be installed to succeed.

        # given
        expected_bundle_name = 'testapplicationartifact'
        # in the template plist file, the name is 'TestApplicationArtifact' (uppercase)

        # Keep our test fixture save - create a copy for tests.
        # - 4DTest_Info.plist is a valid build artifact of a 4D build.
        # - Modified_Info.plist is our temporary working copy which gets modified by tests.
        template_info_plist_file = Path('tests/resources/fixtures/4DTest_Info.plist')
        testing_info_plist_file = Path('tests/resources/temp/Modified_Info.plist')
        testing_info_plist_file.unlink(missing_ok=True)  # cleanup
        shutil.copy(template_info_plist_file, testing_info_plist_file)

        # when
        self.codesign.lowercase_executable_name(testing_info_plist_file)

        # then
        plist: etree_ElementTree = etree.parse(str(testing_info_plist_file))
        top_element: etree_Element = plist.getroot().find('dict')
        actual_bundle_name = top_element.findtext("string[.='%s']" % expected_bundle_name)

        self.assertEqual(expected_bundle_name, actual_bundle_name)

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

    def assertIsUnsigned(self, path_to_item: Path):
        """ Can be called to assert an unsigned item.

        :param path_to_item: Path to the file or bundle whose signature should be verified locally.
        """
        with self.assertRaises(subprocess.SubprocessError) as context:
            verification_result = processes.run_subprocess(
                ['codesign', '--verify', '--deep', '--verbose', path_to_item])
            self.assertEqual(verification_result.returncode, 1)

        self.assertIn('failed', str(context.exception))
        self.assertIn('not signed', str(context.exception))
