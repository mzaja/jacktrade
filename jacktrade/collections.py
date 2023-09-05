from itertools import chain, islice
from typing import Any, Callable, Hashable, Iterable, Iterator, Optional, TypeVar


# ---------------------------------------------------------------------------
# DICTIONARIES
# ---------------------------------------------------------------------------
def _flatten_dict(input_data: dict, output_data: list, max_depth: int) -> None:
    """
    Flattens a nested dict and returns the values inside output_data list.
    Recursion happens until a non-dict item is encountered, or max_depth is reached.
    """
    if isinstance(input_data, dict) and (max_depth > 0):
        for data in input_data.values():
            _flatten_dict(data, output_data, max_depth - 1)
    else:
        output_data.append(input_data)


def flatten_dict(input_data: dict, max_depth: int = 999) -> list:
    """
    Flattens a nested dict and returns the values inside a list.
    Recursion happens until a non-dict item is encountered, or max_depth is reached.
    """
    output_data = []
    _flatten_dict(input_data, output_data, max_depth)
    return output_data


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
def _flatten_list(input_data: list, output_data: list, max_depth: int) -> None:
    """
    Flattens a multilevel list and returns the values inside output_data list.
    Recursion happens until a non-list item is encountered, or max_depth is reached.
    """
    if isinstance(input_data, list) and (max_depth > 0):
        for data in input_data:
            _flatten_list(data, output_data, max_depth - 1)
    else:
        output_data.append(input_data)


def flatten_list(input_data: list, max_depth: int = 999) -> list:
    """
    Flattens a multilevel list and returns the values inside a list.
    Recursion happens until a non-list item is encountered, or max_depth is reached.
    """
    output_data = []
    _flatten_list(input_data, output_data, max_depth)
    return output_data


def chunkify(iterable: Iterable, chunk_size: int = None) -> Iterator[list]:
    """
    Yields successive n-sized list chunks from an iterable.
    Supports generator expressions.
    """
    iterator = iter(iterable)  # Must be assigned here, else infinite loop
    while chunk := list(islice(iterator, chunk_size)):
        yield chunk


def ichunkify(iterable: Iterable, chunk_size: int = None) -> Iterator[Iterator]:
    """
    Yields successive n-sized iterator chunks from an iterable.
    Supports generator expressions.

    WARNING!:   Chunks must be consumed as they are yielded, otherwise
                the results will not be as expected!
    """
    iterator = iter(iterable)
    chunk_size_minus_one = None if (chunk_size is None) else (chunk_size - 1)
    for first_chunk_elem in iterator:
        yield chain([first_chunk_elem], islice(iterator, chunk_size_minus_one))


def limit_iterator(iterable: Iterable, limit: int = None) -> Iterator:
    """
    Returns an interator which yields successive elements of
    the iterable up to the limit, if the limit is specified.
    """
    for count, item in enumerate(iterable, 1):
        if limit and (count > limit):
            return
        yield item


# ---------------------------------------------------------------------------
# MAPPINGS
# ---------------------------------------------------------------------------
T = TypeVar("T")


class BaseMapping(dict):
    """
    Base mapping where each key and value are obtained by applying a getter to
    each item in the iterable.
    """

    def __init__(
        self,
        items: Iterable[T],
        key_getter: Callable[[T], Hashable],
        value_getter: Callable[[T], Any],
        condition: Optional[Callable[[T], bool]] = None,
        skip_exceptions: tuple[type[Exception]] = (),
    ) -> None:
        """
        Parameters:
            - items: An iterable of items of the same type to create a mapping from.
            - key_getter: A function accepting an item and returning a hashable dict key.
            - value_getter: A function accepting an item and returning a dict value.
            - condition: A function accepting an item and returning a boolean value
                         indicating if the item should be included in the mapping.
            - skip_exceptions: A tuple of exceptions which, if they appear during the
                               mapping construction, discard that item instead of raising.
        """
        for item in items:
            try:
                if condition is None or condition(item):
                    self[key_getter(item)] = value_getter(item)
            except skip_exceptions:
                pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({dict(self)})"
