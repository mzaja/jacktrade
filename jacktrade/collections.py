from typing import Iterator, Iterable, Any
from itertools import islice, chain

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
# ITERABLES
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

def chunkify(iterable: Iterable, chunk_size: int) -> Iterator[list]:
    """
    Yields successive n-sized list chunks from an iterable.
    Supports generator expressions.
    """
    iterator = iter(iterable)
    while chunk := list(islice(iterator, chunk_size)):
        yield chunk

def ichunkify(iterable: Iterable, chunk_size: int) -> Iterator[Iterator]:
    """
    Yields successive n-sized iterator chunks from an iterable.
    Supports generator expressions.
    
    WARNING!:   Chunks must be consumed as they are yielded, otherwise
                the results will not be as expected!
    """
    iterator = iter(iterable)
    for first_chunk_elem in iterator:
        yield chain([first_chunk_elem], islice(iterator, chunk_size - 1))

def limited_iterator(iterable: Iterable, limit: int = None) -> Iterator:
    """
    Returns an interator which yields successive elements of
    the iterable up to the limit, if the limit is specified.
    """
    for count, item in enumerate(iterable, 1):
        if limit and (count > limit):
            return
        yield item