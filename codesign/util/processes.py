import subprocess
from subprocess import CompletedProcess
from subprocess import PIPE

from util.logging import LOGGING

logger = LOGGING.getLogger(__name__)


def run_subprocess(commands: list) -> CompletedProcess | CompletedProcess[str]:
    """ Simply runs a subprocess but additionally raises on fail with
    concatenated stdout and stderr.

    :param commands: List of commands and parameters as expected by subprocess.run()
    :return: Result of the completed process (enclosing stdin, stderr, result)
    :raises subprocess.SubprocessError: if command exits with return value != 0
    """
    if not commands:
        raise ValueError('No commands given (empty list)')

    result = subprocess.run(commands,
                            stdout=PIPE,
                            stderr=subprocess.STDOUT,
                            stdin=PIPE,
                            universal_newlines=True)

    if result.returncode != 0:
        raise subprocess.SubprocessError(
            f'{commands[0]} failed with exit code {result.returncode}: {result.stdout.strip()}')

    return result


def popen_simple(commands: list, subject: str) -> subprocess.Popen[str] | subprocess.Popen:
    """ Run a simple subcommand asynchronously and log its output live.

    :param commands: List of commands and arguments as expected in subprocess.Popen
    :param subject: A human-readable subject for that process. Gets printed by the logger.
    :return: Instance of subprocess.Popen that was created when running the process
    :raise SubprocessError: If return code is not equal 0
    """
    # Run asynchronously
    process = subprocess.Popen(commands, stdout=subprocess.PIPE, universal_newlines=True)

    # Poll process.stdout to log its stdout live
    while True:
        output = process.stdout.readline()
        logger.info(output.strip())
        return_code = process.poll()

        if return_code is not None:
            logger.debug('%s return code: %s', subject, return_code)

            # Process has finished, read rest of the output
            for output in process.stdout.readlines():
                logger.info(output.strip())
            break

    if return_code != 0:
        raise subprocess.SubprocessError(
            '%s returned exit code %s' % (subject, str(return_code)))

    return process
