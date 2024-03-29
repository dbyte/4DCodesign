# 4DCodesign
A Python port of Keisuke Miyako's [4d-class-build-application, SignApp.4dm](https://github.com/miyako/4d-class-build-application/blob/main/Project/Sources/Classes/SignApp.4dm) <br>

![owner](https://img.shields.io/badge/%C2%A9-knk%20Business%20Software%20AG-orange)
![licence](https://img.shields.io/badge/license-MIT-brightgreen)
![fourdVersion](https://img.shields.io/badge/4D%20compatibility-v19R4%2B-blue)
![pythonVersion](https://img.shields.io/badge/Python-3.10-blue)

## Docs
Code documentation can be found [here](https://dbyte.github.io/4DCodesign/).

## Preparation
### Codesigning identity
For the signing process and its unit tests to succeed, a valid Apple developer certificate must be installed in the executing machine's keychain.
Its name must begin with "Developer ID Application:". Example: "Developer ID Application: Your Organization (1AB1234567)".
You can optionally pass that name as another argument via command line.
If you omit it, we will search for that pattern in the keychain and the first found entry beginning with "Developer ID Application:" will be selected for the signing process.

### Python dependencies
For XML operations, we decided to use the lxml library for convenient and fast handling.
To install the external dependency

1. cd into ```4DCodesign/codesign```
2. Run ```pip install -r requirements.txt```

## Usage
To run codesigning from the command line, simply

1. Ensure a valid 'Developer ID Application' certificate is installed on the machine
2. cd into project root ```4DCodesign```
3. Run ```python codesign/main.py "Path/to/your/4D-application.app"```<br>
   or
   ```python codesign/main.py "Path/to/your/4D-application.app" "<Your Apple Developer Certificate name>"```

You may pass in 4D standalone, client and server apps.

Default log level is ```INFO```. You can change it by passing a 3rd parameter.
Possible values are ```FATAL, ERROR, WARNING, INFO, DEBUG```.

To trim your personal signing options, have a look at module ```codesign_config``` -->
properties: ```runner_options```, ```default_info_plist_properties```, ```default_hardened_runtime_entitlements```.

Example binding in Azure DevOps CI
![AzureCI_CodesignTask](https://user-images.githubusercontent.com/41309806/214127345-c4dd3dcf-09e9-488d-9b98-030b4626ad40.png)

## Unit tests
### Preparation
1. To run signing integration tests on your 4D `*.app`, you manually need to copy your `*.app` into the dedicated
`4DCodesign/tests/resources/fixtures` directory and rename it to `4D-template-complete.app`.

- This is the expected approach for standalone, client and server type applications. <br>
- However, the file name must always be renamed as described above. <br>
- **Most of the tests will be skipped if you don't do so.**

2. At module tests/testhelper, replace the value of constant DEVELOPER_ID_APPLICATION_ENTRY with the name of your installed
Apple Developer Certificate name, for example ''Developer ID Application: My Company (2YZ3456789)''

### Run unit tests from the command line
To run tests via command line, cd into the project root directory ```4DCodesign``` and

- Run all tests:
  ```python -m unittest discover -v -s tests -t .```

- Run tests for package `core`:
  ```python -m unittest discover -v -s tests.core```

- Run tests for package `util`:
  ```python -m unittest discover -v -s tests.util```

- Run tests in package `util` for module `test_processes.py`:
  ```python -m unittest -v tests.util.test_processes```
