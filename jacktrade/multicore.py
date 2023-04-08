import concurrent.futures
import multiprocessing as mp
from itertools import zip_longest
from typing import Any, Callable, Iterable


# ---------------------------------------------------------------------------
# FUNCTIONS
# ---------------------------------------------------------------------------
def do_multicore_work(
    worker: Callable,
    args: Iterable[tuple] = None,
    kwargs: Iterable[dict] = None,
    worker_done_callback: Callable[[concurrent.futures.Future], Any] = None,
    idle_cpus: int = 0,
):
    """
    Splits the work done by the worker function across multiple CPU cores in a way which
    does not leak memory and uses only the resources required for the active workers.

    WARNING: This function must be run inside 'if __name__ == "__main__":' construct!

    Parameters:
        - worker: A function which does work.
        - args: An iterable containing tuples of positional arguments.
        - kwargs: An iterable containing dictionaries of keyword arguments.
        - worker_done_callback: A function which is called with a Future object as the only
                                parameter as soon as the worker completes assigned work.
        - idle_cpus: How many CPU cores to leave unoccupied. At minimum 1 core will be used.


    NOTE:   This function assumes that the task the worker executes is CPU bound and that
            the operating system will assign each worker to a different core, achieving
            optimal resource usage. However, there is no guarantee this will happen as
            CPU affinity is not explicitly set.
    """
    if not any((args, kwargs)):  # Both are None or empty iterables
        return  # Workers cannot work without arguments
    elif all((args, kwargs)):  # Both are provided
        # Use zip to exit early if iterables do not have the same length
        # and one of them runs out before the other
        workload = zip(args, kwargs)
    else:  # Either args or kwargs are provided, but not both
        workload = zip_longest(args or [], kwargs or [], fillvalue={} if args else ())

    max_workers = max(mp.cpu_count() - idle_cpus, 1)

    with concurrent.futures.ProcessPoolExecutor(max_workers) as executor:
        futures = (executor.submit(worker, *a, **ka) for a, ka in workload)
        for future in concurrent.futures.as_completed(futures):
            if worker_done_callback:
                worker_done_callback(future)
