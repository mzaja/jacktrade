from functools import wraps
from inspect import signature
from typing import Callable


def cached_method(func: Callable):
    """
    Caches a method and attaches the cache to the instance so it gets garbage collected.

    Works with both instance and class methods. When caching a class method, `@classmethod`
    decorator needs to be applied after this one (placed above it).
    """
    cache_name = f"_{func.__name__}_cache"
    func_signature = signature(func)

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if (cache := getattr(self, cache_name, None)) is None:
            setattr(self, cache_name, cache := {})

        # Normalise arguments to avoid cache misses due to differences in ways
        # the arguments are provided when the calls are syntactically the same.
        bound_args = func_signature.bind(self, *args, **kwargs)
        bound_args.apply_defaults()
        key = tuple(bound_args.arguments.values())[1:]  # Exclude 'self'

        try:
            return cache[key]
        except KeyError:
            cache[key] = result = func(self, *args, **kwargs)
            return result

    return wrapper
