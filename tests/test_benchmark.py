import unittest
from time import sleep
from unittest import mock

from jacktrade import CodeTimer


class CodeTimerTest(unittest.TestCase):
    """
    Tests the CodeTimer class.
    """

    def test_core_functionality(self):
        """Tests the core functionality."""
        task_time_s = 0.100
        with CodeTimer() as ct:
            sleep(task_time_s)
        self.assertAlmostEqual(ct.s, task_time_s, 2)
        self.assertAlmostEqual(ct.ms / 1e3, task_time_s, 2)
        self.assertAlmostEqual(ct.us / 1e6, task_time_s, 2)
        self.assertAlmostEqual(ct.ns / 1e9, task_time_s, 2)

    @mock.patch("time.perf_counter_ns")
    def test_resolution(self, mock_perf_counter_ns):
        """Tests that calls are made to the high-resolution nanosecond performance counter."""
        mock_perf_counter_ns.side_effect = [0, 9]
        with CodeTimer() as ct:
            pass
        mock_perf_counter_ns.assert_called()

    @mock.patch("builtins.print")
    def test_print_options(self, mock_print):
        """Tests the no_print option."""
        with CodeTimer(no_print=True) as ct:
            pass
        mock_print.assert_not_called()
        with CodeTimer(no_print=False) as ct:
            pass
        mock_print.assert_called()

    def test_min_digits(self):
        """Tests that the min_digits parameter works as expected."""
        ct = CodeTimer()
        for time_ns in [1, 12, 123, 1234, 12345, 12345678901234567890]:
            for min_digits in range(1, 11):
                with self.subTest(time_ns=time_ns, min_digits=min_digits):
                    digit_count = sum(
                        c.isdigit() for c in ct._format_time(time_ns, min_digits)
                    )
                    self.assertGreaterEqual(digit_count, min_digits)

    @mock.patch("builtins.print")
    def test_decorator(self, mock_print: mock.Mock):
        """Tests that the class can be used as a decorator."""

        @CodeTimer()
        def func():
            return 123

        self.assertEqual(func(), 123)
        mock_print.assert_called_once()
        self.assertIn("Code execution", mock_print.call_args.args[0])

    def test_results_collection(self):
        """Tests storing the benchmark results into a user-provided list."""
        results = []

        @CodeTimer(no_print=True, results=results)
        def sleep_ms(ms: int):
            sleep(ms / 1000)

        sleep_ms(10)
        self.assertAlmostEqual(results[0].ms, 10, delta=2)
        sleep_ms(20)
        self.assertAlmostEqual(results[1].ms, 20, delta=2)
        sleep_ms(30)
        self.assertAlmostEqual(results[2].ms, 30, delta=2)


if __name__ == "__main__":
    unittest.main()
