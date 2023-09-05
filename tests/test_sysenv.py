import platform
import subprocess
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from jacktrade import in_virtual_environment

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


if __name__ == "__main__":
    unittest.main()
