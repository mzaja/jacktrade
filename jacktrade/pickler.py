import pickle
from typing import Any


# ---------------------------------------------------------------------------
# FUNCTIONS
# ---------------------------------------------------------------------------
def pickle_object(obj: Any, filename: str, protocol=None) -> None:
    """
    Pickles the provided Python object and outputs it to the target file.
    """
    with open(filename, "wb") as f:
        pickle.dump(obj, f, protocol=protocol)


def unpickle_object(filename: str) -> Any:
    """
    Unpickles the Python object from a target file and returns it.
    """
    with open(filename, "rb") as f:
        return pickle.load(f)
