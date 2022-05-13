"""
Codesign core objects.
"""
import os
import sys
from typing import Final

# ---------------------------------------------------------------------------
#   Common constants
# ---------------------------------------------------------------------------

IS_WINDOWS: Final[bool] = sys.platform == 'win32'
""" True if current OS is Windows """

IS_MACOS: Final[bool] = sys.platform == 'darwin'
""" True if current OS is macOS """

IS_LINUX: Final[bool] = sys.platform == 'linux'
""" True if current OS is Linux """

IS_RUNNING_AZURE_PIPELINE: bool = True if os.environ.get('TF_BUILD') else False
""" True if an Azure Pipeline called the program, else False.
This environment variable is set by the calling Azure process.
"""
