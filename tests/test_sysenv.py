import platform
import subprocess
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch

from jacktrade import hibernate, in_virtual_environment, restart, shutdown, suspend

PYTHON_CMDS = "import os;import sys;sys.path.insert(0, os.getcwd());from jacktrade import in_virtual_environment;print(in_virtual_environment(),end='');"


class SysenvTest(unittest.TestCase):
    """
    Tests the sysenv module.
    """

    def test_in_virtual_environment(self):
        """
        Tests detecting whether the code is running from a virtual environment.
        """
        in_virtual_environment()  # Hit for code coverage

        with TemporaryDirectory() as tmpd:
            venv_path = Path(tmpd).resolve() / "venv"
            operating_system = platform.system()
            if operating_system == "Windows":
                python = "python"
                sep = " & "
                test_cmd = f'"{venv_path}\\Scripts\\python.exe" -c "{PYTHON_CMDS}"'
            elif operating_system in ("Linux", "Darwin"):
                python = "python3"
                sep = "; "
                test_cmd = f'"{venv_path}/bin/python" -c "{PYTHON_CMDS}"'
            else:
                raise NotImplementedError("Operating system not supported.")
            # Running outside of venv (will not work if launched from venv)
            self.assertEqual(
                subprocess.check_output(
                    f'{python} -c "{PYTHON_CMDS}"', shell=True
                ).decode(),
                "False",
            )
            # Running in venv
            commands = sep.join(
                [
                    f'{python} -m venv "{venv_path}"',
                    test_cmd,
                ]
            )
            self.assertEqual(
                subprocess.check_output(commands, shell=True).decode(), "True"
            )


@patch("subprocess.run")
class PowerManagementTest(unittest.TestCase):
    """
    Tests power management functions.

    Note that, for obvious reasons, these tests do not validate that
    the intended side effect actually occurs, only that a function
    calls a particular command under particular circumstances.
    """

    FUNCTIONS = (suspend, hibernate, shutdown, restart)

    @patch("platform.system", return_value="Windows")
    def test_power_management_windows(self, mock_system: Mock, mock_run: Mock):
        """Tests power management calls on Windows."""
        cmds = (
            "Rundll32.exe Powrprof.dll,SetSuspendState Sleep",
            "shutdown /h",
            "shutdown /s",
            "shutdown /r",
        )
        for func, cmd in zip(self.FUNCTIONS, cmds):
            func()
            mock_run.assert_called_with(cmd)

    @patch("platform.system", return_value="Linux")
    def test_power_management_linux(self, mock_system: Mock, mock_run: Mock):
        cmds = (
            "systemctl suspend",
            "systemctl hibernate",
            "shutdown -h now",
            "shutdown -r now",
        )
        for func, cmd in zip(self.FUNCTIONS, cmds):
            func()
            mock_run.assert_called_with(cmd, shell=True)

    @patch("platform.system", return_value="Mythical")
    def test_power_management_others(self, mock_system: Mock, mock_run: Mock):
        for func in self.FUNCTIONS:
            with self.assertRaisesRegex(NotImplementedError, "Mythical"):
                func()


if __name__ == "__main__":
    unittest.main()
