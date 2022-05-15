"""
Package for unit & integration tests, driven by stubs/fixtures & production data.
To run tests via zsh command line, cd into the project root directory '4DCodesign' and call for example:

- Run ALL tests:
  % python -m unittest discover -v -s tests -t .

- Run all tests for package 'core':
  % python -m unittest discover -v -s tests.core

- Run all tests for package 'util':
  % python -m unittest discover -v -s tests.util

- Run test of module 'test_processes.py' for package 'util':
  % python -m unittest -v tests.util.test_processes
"""
import os
import sys

# This is necessary to be able to run unittests via command line.
# Paths are a view from the root directory '4DCodesign'.
source_root = os.path.abspath('./codesign')
if source_root not in sys.path:
    sys.path.insert(0, source_root)
