import os
import pickle


def pickler(data, filename: str, output_dir: str = None):
    """
    Pickles the provided data and outputs it to the target file. 
    Automatically appends the '.pickle' extension if one is not provided.
    Output directory can be optionally specified.
    """
    EXTENSION = ".pickle"
    if not filename.endswith(EXTENSION):
        filename += EXTENSION
    if output_dir != None:
        filename = os.path.join(output_dir, filename)
    with open(filename, 'wb') as f:
        pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)


def unpickler(filename: str, source_dir: str = None):
    """
    Unpickles data from the target source file, from the source directory.
    """
    if source_dir != None:
        filename = os.path.join(source_dir, filename)
    with open(filename, 'rb') as f:
        return pickle.load(f)    


def param_options_check(param, options: list, param_name: str = '', ignore_case: bool = True):
    """
    Checks if the parameter is one of the options. If not, a ValueError is raised with an error message.
    Parameter name can be provided as an optional argument to display it on error message.
    """
    options_original = options
    param_original = param
    if isinstance(param, str) and ignore_case == True:
        options = [x.lower() if isinstance(x, str) else x for x in options_original]
        param = param_original.lower()
    if param not in options:
        raise ValueError(f"Parameter '{param_name}' must be one of: {options_original}")


def flatten_dict(input_data: dict, output_data: list, max_depth: int = 10):
    """
    Flattens a nested dict by returning its values in a list.
    Recursion happens until a non-dict item is encountered, or max_depth is reached.
    """
    if isinstance(input_data, dict) and (max_depth > 0): 
        [flatten_dict(data, output_data, max_depth - 1) for data in input_data.values()]
    else:
        output_data.append(input_data)

def get_first_dict_item(dictionary: dict) -> tuple:
    """Returns the first (key, value) pair a dictionary."""
    return next(iter(dictionary.items()), None)

def get_first_dict_key(dictionary: dict):
    """Returns the first key in a dictionary."""
    return next(iter(dictionary.keys()), None)

def get_first_dict_value(dictionary: dict):
    """Returns the first value in a dictionary."""
    return next(iter(dictionary.values()), None)

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]