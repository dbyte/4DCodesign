# 4DCodesign
A Python port of Keisuke Miyako's [4d-class-build-application, SignApp.4dm](https://github.com/miyako/4d-class-build-application/blob/main/Project/Sources/Classes/SignApp.4dm) <br>

![owner](https://img.shields.io/badge/%C2%A9-knk%20Business%20Software%20AG-orange)
![licence](https://img.shields.io/badge/license-MIT-brightgreen)
![fourdVersion](https://img.shields.io/badge/4D%20compatibility-v19R4%2B-blue)
![pythonVersion](https://img.shields.io/badge/Python-3.10-blue)

## Preparation
For XML operations, we decided to use the lxml library for convenient and fast handling.
To install the external dependency

1. cd into ```4DCodesign/codesign```
2. Run ```pip install -r requirements.txt```

## Usage
To run codesigning from the command line, simply

1. cd into project root ```4DCodesign```
2. Run ```python codesign/main.py "Path/to/your/4D-application.app"```

You may pass in 4D standalone, client and server apps.

Default log level is INFO. You can change it by passing a 2nd parameter.
Possible values are FATAL, ERROR, WARNING, INFO, DEBUG.

To trim your personal signing options, have a look at module 'codesign_config' -->
properties: runner_options, default_info_plist_properties, default_hardened_runtime_entitlements.

Cheers!

## Unit tests

### Prepare
Coming soon

### Run from the command line
To run tests via command line, cd into the project root directory ```4DCodesign``` and

- Run ALL tests:
  ```python -m unittest discover -v```

- Run all tests for package 'core':
  ```python -m unittest discover -v -s tests.core```

- Run all tests for package 'util':
  ```python -m unittest discover -v -s tests.util```

- Run test of module 'test_processes.py' for package 'util':
  ```python -m unittest -v tests.util.test_processes```
