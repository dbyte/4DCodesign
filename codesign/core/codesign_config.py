import json
import re
from functools import cached_property
from pathlib import Path

from core import IS_MACOS
from util import processes
from util.logging import LOGGING

logger = LOGGING.getLogger(__name__)


class CodesignConfig:
    """ Configuration handler for codesigning. """

    def __init__(self, path_to_app_bundle: Path, signing_identity: str = None, plist_data: dict = None):
        self.path_to_app_bundle: Path = path_to_app_bundle
        """ Qualified path to the 4D application bundle (e.g. /Users/xy/4D/build/out/My4D.app) """

        self.signing_identity: str = \
            signing_identity if signing_identity else self.find_signing_identity('Developer ID Application')  # optional
        """ Optional. Defaults to automatic search for 'Developer ID Application' entry in keychain. """

        self.plist_data: dict | None = plist_data  # optional
        """ Optional; a dict of custom plist data if passed. Defaults to fixed keys which are defined
         at self.default_info_plist_properties """

    def validate(self):
        """ Validates if configuration is valid for signing.
        """
        logger.debug('Validating expectations ... ')

        if not IS_MACOS:
            raise EnvironmentError('This process must be run on macOS')

        if not self.path_to_app_bundle.exists():
            raise ValueError('Path to app bundle does not exist: %s' % self.path_to_app_bundle)

        if self.path_to_app_bundle.is_file():
            raise ValueError('app bundle must be a directory: %s' % self.path_to_app_bundle)

        if self.path_to_app_bundle.suffix != '.app':
            raise ValueError('Suffix ".app" expected for app bundle %s' % self.path_to_app_bundle)

        if 'Developer ID Application:' not in self.signing_identity:
            raise ValueError('Signing identity must contain Developer ID Application certificate name')

        # Log some static properties once
        logger.debug('Default hardened runtime entitlements are: %s',
                     json.dumps(self.default_hardened_runtime_entitlements, indent=4))

        logger.debug('Default Info.plist properties to modify are: %s',
                     json.dumps(self.default_info_plist_properties, indent=4))

        logger.debug('✔️ SUCCESS validating expectations')

    @cached_property
    def runner_options(self) -> dict:
        """ Defines common options for the complete run of the signing process.
        Ordered by call sequence, which is defined within function 'run()'.

        NOTE: These setting are dedicated to our 4D application. Different 4D applications may need
        different settings. Feel free to change them for your needs.

        :return: The common options used while running the signing process.
        """
        options: dict = {
            'removeTempFiles': False,
            'preCleanup': True,

            'signHelpers': False,
            'signNativeComponents': False,
            'signUpdater': False,
            'signFrameworks': False,  # signed by internal 4D signing process, presumably
            'signMobile': False,  # not implemented
            'signInternalComponents': False,  # signed by internal 4D signing process, presumably
            'removeComponentPlugins': False,
            'signPlugins': False,
            'movePluginManifest': False,
            'signComponents': False,
            'signDatabase': True,  # in particular, for lib4d-arm64.dylib - 4D does not sign correctly here (4D v19 R4)
            'signMecab': False,
            'signSASLPlugins': False,
            'signContents': False,
            'removePHP': False,
            'signPHP': False,
            'signBinDirectory': False
        }

        return options

    @cached_property
    def default_info_plist_properties(self) -> dict:
        """ Keys to always insert in Info.plist (UsageDescription) because they can not be added later.
        See: https://developer.apple.com/documentation/bundleresources/information_property_list

        :return: Default properties as dictionary
        """
        properties: dict = {
            'NSRequiresAquaSystemAppearance': 'NO',
            'NSAppleEventsUsageDescription': '',
            'NSCalendarsUsageDescription': '',
            'NSContactsUsageDescription': '',
            'NSRemindersUsageDescription': '',
            'NSCameraUsageDescription': '',
            'NSMicrophoneUsageDescription': '',
            'NSLocationUsageDescription': '',
            'NSPhotoLibraryUsageDescription': '',
            'NSSystemAdministrationUsageDescription': ''
        }

        return properties

    @cached_property
    def default_hardened_runtime_entitlements(self) -> dict:
        """ Hardened Runtime entitlements
        See: https://developer.apple.com/documentation/security/hardened_runtime_entitlements?language=objc

        :return: Default entitlements as dict
        """
        entitlements: dict = {
            # Smartcard access
            'com.apple.security.smartcard': True,

            # Whether app may send Apple Events to other app
            'com.apple.security.automation.apple-events': True,

            # Whether app may be impacted by dyld environment variables
            'com.apple.security.cs.allow-dyld-environment-variables': True,

            # Whether app may create writable and executable memory using the MAP_JIT flag
            'com.apple.security.cs.allow-jit': True,

            # Whether app may create writable and executable memory without using the MAP_JIT flag
            'com.apple.security.cs.allow-unsigned-executable-memory': True,

            # Whether app is a debugger and may attach to other processes or get task ports
            'com.apple.security.cs.debugger': True,

            # Whether to disable code signing protections while launching the app
            'com.apple.security.cs.disable-executable-page-protection': True,

            # Whether app may load plug-ins or frameworks signed by other developers
            'com.apple.security.cs.disable-library-validation': True,

            # Need this for debugging, f.e. 4D-Plugin debugging
            'com.apple.security.get-task-allow': True,  # need this for debugging

            # Whether app may record audio using the built-in microphone and
            # access audio input using Core Audio
            'com.apple.security.device.audio-input': True,

            # Whether app may capture movies and still images using the built-in camera
            'com.apple.security.device.camera': True,

            # Whether app may have read-write access to the user's Photos library
            'com.apple.security.personal-information.photos-library': True,

            # Whether app may access location information from Location Services
            'com.apple.security.personal-information.location': True,

            # Whether app may have read-write access to Contacts in the user's address book
            'com.apple.security.personal-information.addressbook': True,

            # Whether app may have read-write access to the user's calendar
            'com.apple.security.personal-information.calendars': True
        }

        return entitlements

    @staticmethod
    def find_signing_identity(of_type: str) -> str | None:
        """ Finds first name (aka identity) of an installed codesigning-certificate
        whose type must be narrowed by parameter 'of_type'.

        :param of_type: Examples: 'Developer ID Application', 'Developer ID Installer'
        :return: First found identity name, f.e. 'Developer ID Application: Your Organization (1AB1234567)'
        """
        logger.debug('Searching for local codesign identity if type "%s"', of_type)
        result = processes.run_subprocess(['security', 'find-identity', '-p', 'basic', '-v'])

        if matches := re.findall(r'(?m)\s+(\d+\))\s+([0-9a-fA-F]+)\s+\"([^\"]+)\"$', result.stdout):
            for match in matches:
                found_name: str = next((item for item in match if of_type in item), None)
                if found_name:
                    logger.debug('Found local codesign identity for type "%s"', of_type)
                    return found_name

        logger.warning('Did not find local codesign identity for type "%s"', of_type)
        return None
