import json

from betfairlightweight.resources.bettingresources import PriceSize

# monkey patch PriceSize object to print out its value to console
PriceSize.__repr__ = lambda self: f"PriceSize(price={self.price}, size={self.size})"


def pprint(obj):
    """
    Pretty prints the betfairlightweight's _data attribute as JSON
    or the object itself if _data attribute does not exist.
    """
    try:
        print(json.dumps(obj._data, indent=4))
    except AttributeError:
        print(json.dumps(vars(obj), indent=4))


def display_attrs(obj, attrs=None):
    if attrs is None:   # if used as a standalone function
        attrs = [a for a in dir(obj) if not a.startswith('__')]
        print(type(obj))
    if len(attrs) > 0:
        max_len = max(len(a) for a in attrs)
        for attr in attrs:
            print(f"{attr:<{max_len+1}} : {type(getattr(obj, attr))}")


def display_attr_diff(obj1, obj2):
    attr_diff = [x for x in dir(obj1) if x not in dir(obj2)]
    print(f">>> Exclusive to\n{type(obj1)}:")
    display_attrs(obj1, attr_diff)


def display_attr_diffs(obj1, obj2):
    display_attr_diff(obj1, obj2)
    print("\n")
    display_attr_diff(obj2, obj1)


def display_common_attrs(obj1, obj2):
    common_attrs = [x for x in dir(obj1) if (x in dir(obj2)) and (not x.startswith("__"))]
    print(f">>> Common to\n{type(obj1)} AND \n{type(obj2)}:")
    display_attrs(obj1, common_attrs)


def analyse_objects(obj1, obj2 = None):
    """
    Displays the attributes of the two provided objects, 
    their common attributes and their attribute differences.
    """
    display_attrs(obj1)
    print("\n")
    if obj2 is not None:
        display_attrs(obj2)
        print("\n")
        display_common_attrs(obj1, obj2)
        print("\n")
        display_attr_diffs(obj1, obj2)


import time
class CodeTimer:
    
    units = ("ns", "us", "ms", "s")
    
    def __enter__(self):
        self.start = time.perf_counter_ns()
    
    def __exit__(self, exc_type, exc_value, exc_tb):
        finish = time.perf_counter_ns()
        print(f"Code execution took {self.format_time(finish - self.start)}.")

    @classmethod
    def format_time(cls, time_ns: int) -> str:
        """Automatically selecs the suitable time unit and returns a formatted string."""
        divisions = 0
        time_div = time_ns
        while(time_div := time_div // 1000):
            divisions += 1
        return f"{time_ns // (1000 ** divisions)} {cls.units[divisions]}"
