from typing import Iterator, Any, Tuple


# ---------------------------------------------------------------------------
# DICTIONARIES
# ---------------------------------------------------------------------------
def flatten_dict(input_data: dict, output_data: list, max_depth: int = 10) -> None:
    """
    Flattens a nested dict and returns the values inside output_data list.
    Recursion happens until a non-dict item is encountered, or max_depth is reached.
    """
    if isinstance(input_data, dict) and (max_depth > 0): 
        for data in input_data.values():
            flatten_dict(data, output_data, max_depth - 1)
    else:
        output_data.append(input_data)

def get_first_dict_item(dictionary: dict) -> tuple[Any, Any]:
    """Returns the first (key, value) pair a dictionary."""
    return next(iter(dictionary.items()), None)

def get_first_dict_key(dictionary: dict) -> Any:
    """Returns the first key in a dictionary."""
    return next(iter(dictionary.keys()), None)

def get_first_dict_value(dictionary: dict) -> Any:
    """Returns the first value in a dictionary."""
    return next(iter(dictionary.values()), None)

# ---------------------------------------------------------------------------
# LISTS
# ---------------------------------------------------------------------------
def flatten_list(input_data: list, output_data: list, max_depth: int = 10) -> None:
    """
    Flattens a multilevel list and returns the values inside output_data list.
    Recursion happens until a non-list item is encountered, or max_depth is reached.
    """
    if isinstance(input_data, list) and (max_depth > 0): 
        for data in input_data:
            flatten_list(data, output_data, max_depth - 1)
    else:
        output_data.append(input_data)

def chunkify(items: list, chunk_size: int) -> Iterator[list]:
    """Yields successive n-sized chunks from a list of items."""
    for i in range(0, len(items), chunk_size):
        yield items[i : i + chunk_size]