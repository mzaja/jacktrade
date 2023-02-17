# ---------------------------------------------------------------------------
# FUNCTIONS
# ---------------------------------------------------------------------------
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
