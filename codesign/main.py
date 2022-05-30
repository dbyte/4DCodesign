""" Entry point for command line or external code
"""

import sys
from pathlib import Path

from core.codesign import Codesign
from core.codesign_config import CodesignConfig
from util.logging import set_root_loglevel


def main():
    """ To run codesigning, from the command line, simply ::

        1. cd into project root '4DCodesign'
        2. Run this command: python codesign/main.py "Path/to/your/4D-application.app"

    Default log level is INFO. You can change it by passing a 2nd parameter.
    Possible values are **FATAL, ERROR, WARNING, INFO, DEBUG**.

    To trim your personal signing options, have a look at module 'codesign_config' -->
    properties: runner_options, default_info_plist_properties, default_hardened_runtime_entitlements.

    Cheers!
    """
    args: list[str] = sys.argv

    path_to_app_bundle: str = args[1]
    """ Qualified path to the 4D application bundle. Examples:
    /Users/4D/build/out/My4D.app ,
    /Users/4D/build/out/My4D Server.app ,
    /Users/4D/build/out/My4D Client.app
    """

    loglevel_name: str | None = args[2] if len(args) > 2 else 'INFO'
    """ Python log level as string. Optional, defaults to 'INFO'.
    Constraints: FATAL, ERROR, WARNING, INFO, DEBUG
    """

    set_root_loglevel(name=loglevel_name)

    # Create a config instance. Passing signing_identity=None means: Let the Configuration search
    # for the first matching and locally installed "Developer ID Application ..." Certificate.
    # Passing plist_data=None means: Configuration will use its default plist data.
    codesign_config: CodesignConfig = CodesignConfig(
        Path(path_to_app_bundle),
        signing_identity=None,
        plist_data=None)

    # Create a Codesign instance and run codesigning for the given path_to_app_bundle.
    codesign: Codesign = Codesign(codesign_config)
    codesign.run()

    # Note: Exceptions usually won't be caught - we fail early, so there is no need
    # to return a boolean to signal the caller if codesigning succeeded.


if __name__ == '__main__':
    main()
