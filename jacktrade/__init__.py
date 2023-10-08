# Because each submodule is small, there is no need to further subdivide imports
# into categories. Therefore, make everything available from the top-level module,
# like a Swiss army knife.
from .benchmark import CodeTimer
from .buffers import StringBuffers
from .collections import (
    BaseMapping,
    MasterDict,
    Permutations,
    chunkify,
    flatten_dict,
    flatten_list,
    get_first_dict_item,
    get_first_dict_key,
    get_first_dict_value,
    ichunkify,
    limit_iterator,
)
from .files import merge_csv_files
from .multicore import do_multicore_work
from .pickler import pickle_object, unpickle_object
from .sysenv import hibernate, in_virtual_environment, restart, shutdown, suspend
