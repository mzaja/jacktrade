from functools import wraps
from typing import Callable


def cached_method(func: Callable):
    """
    Caches a method and attaches the cache to the instance so it gets garbage collected.

    Works with both instance and class methods. When caching a class method, `@classmethod`
    decorator needs to be applied after this one (placed above it).
    """
    cache_name = f"_{func.__name__}_cache"

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        # Keyword arguments are sorted to ensure their order does not matter
        key = (args, tuple(sorted(kwargs.items(), key=lambda x: x[0])))

        if (cache := getattr(self, cache_name, None)) is None:
            setattr(self, cache_name, cache := {})

        if key in cache:
            return cache[key]

        result = cache[key] = func(self, *args, **kwargs)
        return result

    return wrapper
