import os.path
import pickle
from typing import Any


# ---------------------------------------------------------------------------
# FUNCTIONS
# ---------------------------------------------------------------------------
def pickler(
    data: Any, filename: str, output_dir: str = None, extension=".pickle", protocol=None
) -> None:
    """
    Pickles the provided data and outputs it to the target file in the
    output directory. Appends the '.pickle' extension by default.
    """
    if extension:
        filename += extension
    if output_dir:
        filename = os.path.join(output_dir, filename)
    with open(filename, "wb") as f:
        pickle.dump(data, f, protocol=protocol)


def unpickler(filename: str, source_dir: str = None) -> Any:
    """
    Unpickles data from the target source file, from the source directory.
    """
    if source_dir:
        filename = os.path.join(source_dir, filename)
    with open(filename, "rb") as f:
        return pickle.load(f)
