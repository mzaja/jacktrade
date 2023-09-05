import unittest
from multiprocessing import cpu_count
from unittest import mock

from jacktrade import do_multicore_work

# ---------------------------------------------------------------------------
# TEST FIXTURES
# ---------------------------------------------------------------------------
NUMBERS = [1, 2, 3, 4, 5]
LETTERS = ["a", "b", "c", "d", "e"]
COMBINED = list(zip(NUMBERS, LETTERS))


def worker(first, second) -> tuple:
    """
    Sample worker to be deployed on multiple cores.
    Receives two arguments and returns them as a tuple.
    """
    return (first, second)


# ---------------------------------------------------------------------------
# TEST CASES
# ---------------------------------------------------------------------------
class MulticoreTest(unittest.TestCase):
    """
    Tests the multicore submodule.
    """

    def setUp(self) -> None:
        self.results = []

    def worker_done_callback(self, future):
        """Called when a worker finishes execution."""
        self.results.append(future.result())

    def test_no_args_or_kwargs_provided(self):
        """Tests that the function exits gracefully if no args or kwargs are provided."""
        do_multicore_work(worker)  # if It doesn't raise an exception, the test passes

    def test_args_provided(self):
        """Tests providing positional arguments to the worker."""
        do_multicore_work(
            worker,
            args=zip(NUMBERS, LETTERS),
            worker_done_callback=self.worker_done_callback,
        )
        self.assertEqual(set(self.results), set(COMBINED))

    def test_kwargs_provided(self):
        """Tests providing positional arguments to the worker."""
        do_multicore_work(
            worker,
            kwargs=[{"first": x, "second": y} for x, y in zip(NUMBERS, LETTERS)],
            worker_done_callback=self.worker_done_callback,
        )
        self.assertEqual(set(self.results), set(COMBINED))

    def test_args_and_kwargs_provided(self):
        """Tests providing positional arguments to the worker."""
        do_multicore_work(
            worker,
            args=zip(NUMBERS),  # zip will "tuplify" the list's elements
            kwargs=[{"second": y} for y in LETTERS],
            worker_done_callback=self.worker_done_callback,
        )
        self.assertEqual(set(self.results), set(COMBINED))

    @mock.patch("concurrent.futures.as_completed")
    @mock.patch("concurrent.futures.ProcessPoolExecutor")
    def test_idle_cpus(self, mock_executor, mock_as_completed):
        """Tests the use of idle_cpus parameter."""
        # Test params are (idle_cpus, max_workers)
        test_params = [(1, max(cpu_count() - 1, 1)), (cpu_count() + 1, 1)]
        for idle_cpus, max_workers in test_params:
            with self.subTest(idle_cpus=idle_cpus, max_workers=max_workers):
                mock_as_completed.return_value = []
                do_multicore_work(
                    worker, args=zip(NUMBERS, LETTERS), idle_cpus=idle_cpus
                )
                mock_executor.assert_called_with(max_workers)


if __name__ == "__main__":
    unittest.main()
