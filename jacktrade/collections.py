from itertools import chain, islice, product
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


class MasterDict:
    """
    Holds multiple dicts and provides a simple method to delete keys and values from them all.

    This object is usually used to hold caches, which can then be reliably emptied with
    a single method call to prevent memory leaks.

    Despite the name, this class is not a dict subtype. However, it can be converted to a
    dict using as_dict() method.
    """

    def __init__(self, **subdicts: dict) -> None:
        """
        Initialises the master dict with sub-dicts, which are provided as keyword
        arguments. Argument name is the dict name, while value is the dict object.
        """
        for attr, value in subdicts.items():
            setattr(self, attr, value)

    def delete_keys(self, *keys: Hashable) -> None:
        """Deletes provided keys from all sub-dictionaries where they are present."""
        for key in keys:
            for subdict in self:
                subdict.pop(key, None)

    def clear_all(self) -> None:
        """Clears all sub-dicts."""
        for subdict in self:
            subdict.clear()

    def as_dict(self) -> dict[str, dict]:
        """
        Returns a dictionary representation of itself, where keys are sub-dict names and
        values are sub-dict objects.
        """
        return vars(self)

    def __repr__(self) -> str:
        return (
            self.__class__.__name__
            + "("
            + ", ".join(f"{n}={d}" for n, d in vars(self).items())
            + ")"
        )

    def __iter__(self) -> Iterator[dict]:
        """Iterates over sub-dicts."""
        return iter(vars(self).values())


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

    def invert(self, strict: bool = False) -> dict:
        """
        Returns an inverse mapping of values to keys.

        When strict=True, ValueError is raised if the values cannot be unambiguously
        mapped to keys because they are not unique.
        """
        if strict and len(set(self.values())) != len(self):
            raise ValueError("Dict values are not unique.")
        return {v: k for k, v in self.items()}

    def _invert_and_cast(self, new_type: type[dict], strict: bool) -> dict:
        """
        Inverts the keys and values in the dictionary and returns them as a custom mapping type.

        This method is generally reserved for use with BaseMapping subclasses, when the inverse
        BaseMapping subclass instance is another BaseMapping subclass instance.
        """
        inverse_mapping = new_type([])
        # BaseMapping must be provided explicitly here to avoid infinite recursion
        inverse_mapping.update(BaseMapping.invert(self, strict))
        return inverse_mapping


# ---------------------------------------------------------------------------
# COMBINATORICS
# ---------------------------------------------------------------------------
class Permutations:
    """
    Yields all possible combinations of the named input parameters,
    returning them as positional (tuple) or keyword (dict) arguments.

    For example:
    ```py
    p = Permutations(a=[1, 2, 3], b=["A", "B"])
    for kwargs in p:
        # yields:
        # {"a": 1, "b": "A"}
        # {"a": 1, "b": "B"}
        # {"a": 2, "b": "A"}
        # {"a": 2, "b": "B"}
        # ...
    ```
    """

    def __init__(self, **kwargs: Iterable):
        self._kwargs = kwargs
        self._names = tuple(kwargs.keys())
        self._combinations = tuple(product(*kwargs.values()))

    @property
    def args(self) -> list[tuple]:
        """Lists all combinations as tuples (positional arguments)."""
        return list(self._combinations)

    @property
    def kwargs(self) -> list[dict[str, Any]]:
        """Lists all combinations as dicts (keyword arguments)."""
        return list(self)

    def __iter__(self) -> Iterator[dict[str, Any]]:
        """
        Yields a kwarg dictionary with all possible combinations of input parameters.
        """
        for values in self._combinations:
            yield dict(zip(self._names, values))

    def __len__(self) -> int:
        return len(self._combinations)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._kwargs}"
