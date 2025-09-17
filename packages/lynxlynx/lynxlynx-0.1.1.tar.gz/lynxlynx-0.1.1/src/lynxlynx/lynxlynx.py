"""Utility library"""

import logging
import subprocess

from termcolor import colored


class CommandOutput:
	"""Class for shell command output.

	Args:
		returnCode: Linux Exit Code (0-255)
		stdOut: Linux STDOUT
		stdErr: Linux STDERR
		args: Commands that were ran
	"""

	def __init__(
		self,
		*,
		returnCode: int,
		stdOut: str,
		stdErr: str,
		args: list[str],
	) -> None:
		"""Init self."""
		super().__init__()
		self.returnCode = returnCode
		self.stdOut = stdOut
		self.stdErr = stdErr
		self.args = args


class ShellExecError(Exception):
	"""Throw a specific exception, no special handling."""
	def __init__(self, stdOut: str, stdErr: str, returnCode: int) -> None:
		"""Init with params"""
		super().__init__()
		self.stdOut = stdOut
		self.stdErr = stdErr
		self.returnCode = returnCode


def shellExec(
	*,
	args: list[str],
	timeout: int = 150,
	start_new_session: bool = False,
	communicate: bool = True,
) -> tuple[CommandOutput, list[str] | None]:
	"""Execute a shell command with subprocess.

	Args:
		args: Command and arguments to execute.
		timeout: Maximum time in seconds to wait for the command to complete.
		start_new_session: Whether to run the process in the background, if not, it will die together with Python
		communicate: Attempt comms with the process - it will block if true

	Returns:
		CommandOutput: An object containing the returncode, stdout, and stderr.

	Raises:
		ShellExecError: If an error occurs during command execution.

	"""
	logging.debug(f"Executing command: {' '.join(args)}")
	stdout: bytes | str | None = ""
	stderr: bytes | str | None = ""
	with subprocess.Popen(
		args,
		stdout=subprocess.PIPE,
		stderr=subprocess.PIPE,
		text=True,
		start_new_session=start_new_session,
	) as process:
		errorList: list[str] = []
		if not communicate:
			return (CommandOutput(args=args, returnCode=0, stdOut="", stdErr=""), [])
		try:
			stdout, stderr = process.communicate(timeout=timeout)
			# print(vars(process))
		except subprocess.TimeoutExpired as timedOutProcess:
			logging.warning(f"timedoutproctimeout is {timedOutProcess.stdout}; stderr is {timedOutProcess.stderr}")
			process.kill()
			stdout, stderr = timedOutProcess.stdout, timedOutProcess.stderr
			# stdout, stderr = process.communicate(timeout=timeout)
			# logging.warning(f"timedoutproctimeout postkill is {stdout}; stderr is {stderr}")
			logging.error(
				f"Command '{' '.join(args)}' timed out after {timeout} seconds, user probably ignored notification."
			)
			errorList.append("Timeout")
			raise ShellExecError(str(stdout) if stdout else "", str(stderr) if stderr else "", process.returncode) from timedOutProcess
		except subprocess.SubprocessError as e:
			process.kill()
			# stdout, stderr = process.communicate(timeout=timeout) # Is this useful? Needs testing
			logging.critical(f"An error occurred while executing command '{' '.join(args)}'.")
			errorList.append("Subprocess")
			raise ShellExecError(str(stdout) if stdout else "", str(stderr) if stderr else "", process.returncode) from e
		except Exception as e:
			logging.exception("Unknown exception trying to run a command!")
			raise ShellExecError(str(stdout) if stdout else "", str(stderr) if stderr else "", process.returncode) from e

	# if stdout is None:
	# stdout = ''
	# elif isinstance(stdout, bytes):
	# stdout = stdout.strip().decode('utf-8')
	# else:
	stdout = stdout.strip()

	# if stderr is None:
	# stderr = ''
	# elif isinstance(stderr, bytes):
	# stderr = stderr.strip().decode('utf-8')
	# else:
	stderr = stderr.strip()

	return (CommandOutput(args=args, returnCode=process.returncode, stdOut=stdout, stdErr=stderr), errorList)


# Alias, deprecate shell_exec
shell_exec = shellExec


def printCommandOutput(*, commandOutput: CommandOutput) -> None:
	"""Pretty print command output info"""
	if commandOutput.stdOut:
		print(colored(f"{' '.join(commandOutput.args)} STDOUT:\n{commandOutput.stdOut}", "yellow"))
	if commandOutput.stdErr:
		print(colored(f"{' '.join(commandOutput.args)} STDERR:\n{commandOutput.stdErr}", "red"))


def convert_to_unicode(*, input_str: str) -> str:
	"""Convert string to its unicode representation."""
	return "".join(f"\\u{ord(c):04x}" for c in input_str)


if __name__ == "__main__":
	logging.debug("Input: hello")
	logging.debug(f"Output: {convert_to_unicode(input_str='hello')}")
