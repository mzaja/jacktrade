# jacktrade
[![PyPI version](https://badge.fury.io/py/jacktrade.svg)](https://badge.fury.io/py/jacktrade) ![License](https://img.shields.io/github/license/mzaja/jacktrade)

**Jack of all trades, master of none** - a collection of commonly used Python utilities. Install using:
```
pip install jacktrade
```

The package consists of the following submodules:

- [Benchmark](#benchmark)
- [Collections](#collections)
- [Multicore](#multicore)
- [Pickler](#pickler)

## Benchmark
Contains a `CodeTimer` class which is used to elegantly and precisely time a piece of code:
```py
from jacktrade.benchmark import CodeTimer
from time import sleep

with CodeTimer() as ct:
    # Enter code to time here
    sleep(0.1)  # Simulate a piece of code

# "Code execution took 100 ms." gets printed out.
```

## Collections
Contains utility functions for working with collections, namely dictionaries and iterables. Usage examples include:
```py
from jacktrade.collections import *

# Dict utilities
dict_data = {"a": 1, "b": {"c": 2}}
flatten_dict(dict_data)             # Returns: [1, 2]
get_first_dict_item(dict_data)      # Returns: ("a", 1)
get_first_dict_key(dict_data)       # Returns: "a"
get_first_dict_value(dict_data)     # Returns: 1

# Iterable utilities
list_data = [1, 2, [3, 4], 5, 6]
flatten_list(list_data)                     # Returns: [1, 2, 3, 4, 5, 6]
list(chunkify(list_data, chunk_size=2))     # Returns: [[1, 2], [[3, 4], 5], [6]]
list(limit_iterator(list_data, limit=3))    # Returns: [1, 2, [3, 4]]
```

## Multicore
Provides an elegant and memory-efficient way to process data using multiple cores. The main advantage of using `do_multicore_work` function over manually using `concurrent.futures` or `multiprocessing` modules is that new jobs are only submitted for execution when a CPU core is available. This optimises CPU and RAM usage. Using the aforementioned modules directly, it is all too easy to inadvarently cause memory leaks and crash the interpreter (if not the whole system).

Usage example (does not work in the interactive interpreter):
```py
from jacktrade.multicore import do_multicore_work

def worker(first, second) -> tuple:
    """
    Receives two arguments and returns them as a tuple.
    """
    return (first, second)

def worker_done_callback(future):
    """Called whenever a worker process terminates and returns a result."""
    print(future.result())

if __name__ == "__main__":
    do_multicore_work(
        worker, args=[(1, 2), (3, 4), (5, 6)], worker_done_callback=worker_done_callback
    )    # Prints: (1, 2)\n(3, 4)\n(5, 6)\n
```

## Pickler
This tiny module contains two convenience functions for pickling and unpickling Python objects, making it possible to do so with a single function call (a feature missing from `pickle` module):
```py
from jacktrade.pickler import pickle_object, unpickle_object

pickle_object(obj := [1, 2, 3], filename := "obj.pickle")   # Pickles obj to obj.pickle file
assert unpickle_object(filename) == obj     # Unpickle obj.pickle and test equality with obj
```
