import re
import subprocess
from unittest import TestCase

from util import processes
from util.logging import set_root_loglevel


class TestProcesses(TestCase):
    """ Test processes utilities """

    @classmethod
    def setUpClass(cls) -> None:
        set_root_loglevel(name='INFO')

    def test_run_subprocess__runsAsExpectedIfValidCommandIsPassed(self):
        # given
        command = ['python', '--version']

        # when
        result = processes.run_subprocess(command)

        # then
        # Expect a Python version string on stdout, like "Python 3.10.0"
        self.assertRegex(result.stdout.strip(), re.compile(r'^Python \d+(\.\d+){2,3}$'))

    def test_run_subprocess__raisesOnCommandLineErrorAndIncludesStderrInMessage(self):
        # given
        invalid_command = ['python', '--somenonexistingparam']

        # when
        with self.assertRaises(subprocess.SubprocessError) as context:
            processes.run_subprocess(invalid_command)

        # then
        # Expect the following fragment within the raised error message
        self.assertIn('python failed with exit code 2: unknown option', str(context.exception))

    def test_popen_simple__logsOutputAsExpectedIfValidCommandIsPassed(self):
        # given
        command = ['python', '--version']

        # Expect a Python version string on stdout, like "Python 3.10.0"
        with self.assertLogs('util.processes', level='INFO') as logger_context:
            # when
            processes.popen_simple(command, subject='Some happy path unit test for popen_simple')

            # then
            log_messages: list = logger_context.output
            self.assertGreaterEqual(len(log_messages), 1)
            self.assertRegex(log_messages[0], re.compile(r'Python \d+(\.\d+){2,3}$'))

    def test_popen_simple__raisesOnCommandLineErrorAndIncludesStderrInMessage(self):
        # given
        invalid_command = ['python', '--somenonexistingparam']
        expected_subject = 'Some unit test for failing popen_simple'

        # when
        with self.assertRaises(subprocess.SubprocessError) as context:
            processes.popen_simple(invalid_command, subject=expected_subject)

        # then
        # Expect the following fragment within the raised error message
        self.assertIn(expected_subject, str(context.exception))
