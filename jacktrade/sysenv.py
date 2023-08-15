import sys


def in_virtual_environment() -> bool:
    """
    Returns True if called from a virtual environment, else False.
    """
    # https://docs.python.org/3/library/venv.html#how-venvs-work
    # sys.base_prefix: Always points to the Python installation directory.
    # sys.prefix: Points to either venv or installation directory.
    return sys.prefix != sys.base_prefix
