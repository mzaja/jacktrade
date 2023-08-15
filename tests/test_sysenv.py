import unittest
from tempfile import TemporaryDirectory
import subprocess
import platform
from pathlib import Path

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
        # Not running in venv (will not work if launched from venv)
        self.assertEqual(
            subprocess.check_output(f'python -c "{PYTHON_CMDS}"').decode(), "False"
        )
        # Running in venv
        with TemporaryDirectory() as tmpd:
            venv_path = str(Path(tmpd) / "venv")
            cmd_install_venv = f'python -m venv "{venv_path}"'
            operating_system = platform.system()
            if operating_system == "Windows":
                commands = " & ".join(
                    [
                        cmd_install_venv,
                        f'{venv_path}\\Scripts\\python.exe -c "{PYTHON_CMDS}"',
                    ]
                )
            elif operating_system in ("Linux", "Darwin"):  # Darwin is MacOS
                commands = "; ".join(
                    [
                        cmd_install_venv,
                        f'source {venv_path}/bin/python -c "{PYTHON_CMDS}"',
                    ]
                )
            else:
                raise NotImplementedError("Operating system not supported.")
            self.assertEqual(
                subprocess.check_output(commands, shell=True).decode(), "True"
            )


if __name__ == "__main__":
    unittest.main()
