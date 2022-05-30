import shutil
import unittest
from pathlib import Path
from unittest import TestCase

from core import IS_WINDOWS
from core.codesign_config import CodesignConfig
from tests.testhelper import create_temp_testing_dir, DEVELOPER_ID_APPLICATION_ENTRY
from util.logging import set_root_loglevel


@unittest.skipIf(IS_WINDOWS, 'Not applicable for Windows')
class TestCodesignConfig(TestCase):
    """ Unit tests for class CodesignConfig """

    @classmethod
    def setUpClass(cls) -> None:
        set_root_loglevel(name='INFO')

    def setUp(self) -> None:
        # Cleanup the 'temp' testing-directory and create a new one.
        temp_dir: Path = create_temp_testing_dir()
        # Create stub of an .app bundle
        path_to_bundle_stub = temp_dir / 'Test.app'
        # Finally, create the stub for tests with root Test.app
        path_to_bundle_stub.mkdir()

        # Create the instance under test
        self.config: CodesignConfig = \
            CodesignConfig(path_to_bundle_stub, signing_identity=DEVELOPER_ID_APPLICATION_ENTRY, plist_data=None)

    def tearDown(self) -> None:
        # Cleanup
        del self.config
        # Note: We do not remove the 'temp' directory at tearDown - for manual inspection purposes.
        # It gets removed/created within the setUp phase.

    def test_validate__raisesIfGivenBundleNotExists(self):
        shutil.rmtree(self.config.path_to_app_bundle, ignore_errors=True)

        # given
        self.config.path_to_app_bundle = Path('./NonExisting.app')

        # when
        with self.assertRaises(ValueError) as context:
            self.config.validate()

        # then
        self.assertIn('does not exist', str(context.exception))

    def test_validate__raisesIfGivenBundleIsFile(self):
        shutil.rmtree(self.config.path_to_app_bundle, ignore_errors=True)

        # given
        new_path = self.config.path_to_app_bundle.parent / 'SomeFile.png'
        new_path.touch()
        self.config.path_to_app_bundle = new_path

        # when
        with self.assertRaises(ValueError) as context:
            self.config.validate()

        # then
        self.assertIn('must be a directory', str(context.exception))

        # Cleanup
        new_path.unlink()

    def test_validate__raisesIfGivenBundleHasWrongSuffix(self):
        shutil.rmtree(self.config.path_to_app_bundle, ignore_errors=True)

        # given
        given_path = self.config.path_to_app_bundle.parent / 'TestApp.wrong'
        self.config.path_to_app_bundle = given_path
        self.config.path_to_app_bundle.mkdir()

        # when
        with self.assertRaises(ValueError) as context:
            self.config.validate()

        # then
        self.assertIn('Suffix', str(context.exception))

    def test_validate__raisesOnSigningIdentityMismatch(self):
        # given
        self.config.signing_identity = 'Wrong identity string'

        # when
        with self.assertRaises(ValueError) as context:
            self.config.validate()

        # then
        self.assertIn('must contain Developer ID', str(context.exception))

    def test_find_signing_identity__returnsFirstFoundIdentityIfCertificateIsInstalled(self):
        # Note that a valid "Developer ID Application: ..." Certificate must be installed to succeed.

        # given
        given_identity_type: str = 'Developer ID Application'

        # when
        identity_name = self.config.find_signing_identity(of_type=given_identity_type)

        # then
        self.assertIsNotNone(identity_name)

    def test_find_signing_identity__returnsNoneIfCertificateDoesNotExist(self):
        # Note that a valid "Developer ID Application: ..." Certificate must be installed to succeed.

        # given
        given_identity_type: str = 'This certificate type does not exist'

        # when
        identity_name = self.config.find_signing_identity(of_type=given_identity_type)

        # then
        self.assertIsNone(identity_name)
