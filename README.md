# jacktrade
[![test](https://github.com/mzaja/jacktrade/actions/workflows/test.yml/badge.svg)](https://github.com/mzaja/jacktrade/actions/workflows/test.yml) [![Coverage Status](https://coveralls.io/repos/github/mzaja/jacktrade/badge.svg?branch=main)](https://coveralls.io/github/mzaja/jacktrade?branch=main) [![PyPI version](https://img.shields.io/pypi/v/jacktrade)](https://pypi.org/project/jacktrade/) ![Python version](https://img.shields.io/pypi/pyversions/jacktrade) [![License](https://img.shields.io/github/license/mzaja/jacktrade)](https://github.com/mzaja/jacktrade/blob/main/LICENSE.md)

**Jack of all trades, master of none** - a collection of commonly used Python utilities. Install using:
```
pip install jacktrade
```

The package consists of the following submodules:

- [Benchmark](#benchmark)
- [Buffers](#buffers)
- [Collections](#collections)
- [Files](#files)
- [Multicore](#multicore)
- [Pickler](#pickler)
- [Sysenv](#sysenv)

## Benchmark
Contains a `CodeTimer` class which is used to elegantly and precisely time a piece of code:
```py
from jacktrade import CodeTimer
from time import sleep

with CodeTimer() as ct:
    # Enter code to time here
    sleep(0.1)  # Simulates a piece of code

# Prints: "Code execution took 100 ms."
(ct.ns, ct.us, ct.ms, ct.s)  # Access code duration in nano/micro/milli/seconds.
```

A `CodeTimer` instance can also be used as a decorator and store results of repeated function calls inside the list provided as `results` argument:
```py
from jacktrade import CodeTimer
from time import sleep

results = []  # A list for storing timing results

@CodeTimer(no_print=True, results=results)
def sleep_ms(milliseconds: int):
    sleep(milliseconds / 1000)

sleep_ms(100)  # Call wrapped function
sleep_ms(200)  # Call again
print(int(results[0].ms))  # Prints: "100"
print(int(results[1].ms))  # Prints: "200"
```

## Buffers
Contains a `StringBuffers` class, whose purpose is to reduce the number of I/O operations
when writing to files. By speficying `buffer_size` parameter, the contents of the buffer
are automatically flushed to disk when the buffer fills up. The class handles any number
of simultaneously "open" files.

```py
from jacktrade import StringBuffers

output_file = "out.txt"
buffers = StringBuffers(output_dir="text", buffer_size=3)
buffers.add(output_file, "Hello")   # Nothing is written out
buffers.add(output_file, " world")  # Nothing is written out
buffers.add(output_file, "!")  # "Hello world!" is written to ./text/out.txt
```

## Collections
Contains utility functions for working with collections, namely dictionaries and iterables. Usage examples include:
```py
from jacktrade import *

# Dict utilities
dict_data = {"a": 1, "b": {"c": 2}}
flatten_dict(dict_data)             # Returns: [1, 2]
get_first_dict_item(dict_data)      # Returns: ("a", 1)
get_first_dict_key(dict_data)       # Returns: "a"
get_first_dict_value(dict_data)     # Returns: 1

# Iterable utilities
list_data = [1, 2, [3, 4], 5, 6]
flatten_list(list_data)             # Returns: [1, 2, 3, 4, 5, 6]
chunkify(list_data, chunk_size=2)   # Yields: [1, 2], [[3, 4], 5], [6]
limit_iterator(list_data, limit=3)  # Yields: 1, 2, [3, 4]
```

`MasterDict` is a wrapper class holding multiple dictionaries. It provides methods for simultaneously deleting keys from all underlying dictionaries, as well as clearing them. It is intended to hold caches and reliably empty them with a single method call.
```py
from jacktrade import MasterDict

dicts = MasterDict(a={1: "1", 2: "2"}, b={1: "1", 3: "3"}, c={4: "4"})
dicts.delete_keys(1, 3)  # Delete keys 1 and 3 from all dictionaries
dicts.as_dict()  # Returns:  {'a': {2: '2'}, 'b': {}, 'c': {4: '4'}}
dicts.clear_all()  # Clear all dictionaries
dicts.as_dict()  # Returns:  {'a': {}, 'b': {}, 'c': {}}
```

`BaseMapping` is a generic base class used to create `dict` subclasses which automatically map keys to values from a collection of objects of the same type. It is used like so:
```py
from jacktrade import BaseMapping

class NameAgeLookup(BaseMapping):
    """
    Maps a person's name to its age if the person is over 18 years old.
    """

    def __init__(self, persons):
        super().__init__(
            items=persons,
            key_getter=lambda p: p["name"],
            value_getter=lambda p: p["age"],
            condition=lambda p: p["age"] > 18,
        )

mapping = NameAgeLookup(
    [
        {"name": "Jack", "age": 15},
        {"name": "Mike", "age": 27},
        {"name": "Pete", "age": 39},
    ]
)

# Assertions pass
assert mapping == {"Mike": 27, "Pete": 39}
assert mapping.invert() == {27: "Mike", 39: "Pete"}
```

`Permutations` class is used for parametrisation, returning all possible combinations of input parameters:
```py
from jacktrade import Permutations

p = Permutations(a=[1, 2, 3], b=["A", "B"])
p.args    # Returns: [(1, "A"), (1, "B"), (2, "A"), (2, "B"), ...]
p.kwargs  # Returns: [{"a": 1, "b": "A"}, {"a": 1, "b": "B"}, ...]
for kwargs in p:
    # yields:
    # {"a": 1, "b": "A"}
    # {"a": 1, "b": "B"}
    # ...
```

## Files
Provides utilities for working with files. Currently it contains only a single function for merging CSV files.
```py
from jacktrade import merge_csv_files

# Merges A.csv and B.csv into AB.csv without duplicating headers
merge_csv_files(["A.csv", "B.csv"], "AB.csv")

# Merges A.csv and B.csv into AB.csv verbatim, treating headers as data
merge_csv_files(["A.csv", "B.csv"], "AB.csv", has_headers=False)
```

## Multicore
Provides an elegant and memory-efficient way to process data using multiple cores. The main advantage of using `do_multicore_work` function over manually using `concurrent.futures` or `multiprocessing` modules is that new jobs are only submitted for execution when a CPU core is available. This optimises CPU and RAM usage. Using the aforementioned modules directly, it is all too easy to inadvarently cause memory leaks and crash the interpreter (if not the whole system).

Usage example (does not work in the interactive interpreter):
```py
from jacktrade import do_multicore_work

def worker(first, second) -> tuple:
    """Receives two arguments and returns them as a tuple."""
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
from jacktrade import pickle_object, unpickle_object

pickle_object(obj := [1, 2, 3], filename := "obj.pickle")   # Pickles obj to obj.pickle file
assert unpickle_object(filename) == obj     # Unpickle obj.pickle and test equality with obj
```

## Sysenv
Contains utilities for interacting with the operating system and the environment.
```py
from jacktrade import in_virtual_environment, suspend, hibernate, restart, shutdown

# Power management
suspend()    # Put the machine into standby
hibernate()  # Hibernate the machine
restart()    # Restart the machine
shutdown()   # Shut down the machine

# Miscellaneous
in_virtual_environment()  # True if called inside venv, else False
```
