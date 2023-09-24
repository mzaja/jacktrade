import platform
import subprocess
import sys


def in_virtual_environment() -> bool:
    """
    Returns True if called from a virtual environment, else False.
    """
    # https://docs.python.org/3/library/venv.html#how-venvs-work
    # sys.base_prefix: Always points to the Python installation directory.
    # sys.prefix: Points to either venv or installation directory.
    return sys.prefix != sys.base_prefix


def _execute_os_specific_commands(windows_cmd: str = None, linux_cmd: str = None):
    """Executes OS-specific commands depending on the current platform."""
    match platform.system():
        case "Windows" if windows_cmd:
            subprocess.run(windows_cmd)
        case "Linux" if linux_cmd:
            subprocess.run(linux_cmd, shell=True)
        case str(p):
            raise NotImplementedError(f"System '{p}' is not supported.")


def suspend() -> None:
    """
    Puts the machine into standby. "sleep" on Windows and "suspend" on Linux.
    """
    _execute_os_specific_commands(
        "Rundll32.exe Powrprof.dll,SetSuspendState Sleep", "systemctl suspend"
    )


def hibernate() -> None:
    """Puts the machine into hibernation."""
    _execute_os_specific_commands("shutdown /h", "systemctl hibernate")


def shutdown() -> None:
    """Shuts down the machine."""
    _execute_os_specific_commands("shutdown /s", "shutdown -h now")


def restart() -> None:
    """Restarts the machine."""
    _execute_os_specific_commands("shutdown /r", "shutdown -r now")
