import re
import unittest
from time import sleep
from unittest import mock

from jacktrade import CodeTimer
from jacktrade.benchmark import *


class CodeTimerTest(unittest.TestCase):
    """
    Tests the CodeTimer class.
    """

    @staticmethod
    def flaky(test_method):
        """
        Marks the test as flaky, and suppresses AssertionError
        when running Python <= 3.10 on Windows.

        Prior to Python 3.11, the accuracy of sleep() on Windows was
        much lower, and millisecond accuracy is not reliably attainable.
        https://docs.python.org/3.11/library/time.html#time.sleep
        """

        def wrapper(self: unittest.TestCase, *args, **kwargs):
            try:
                test_method(self, *args, **kwargs)
            except AssertionError as ex:
                import platform
                import sys

                # Exemption for Python <= 3.10 running on Windows
                if sys.version_info[:2] <= (3, 10) and platform.system() == "Windows":
                    self.skipTest(
                        "sleep() function is insufficiently accurate on this platform"
                    )
                else:
                    raise ex  # Fail in all other cases

        return wrapper

    @flaky
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

    @mock.patch("time.perf_counter_ns")
    def test_resolution(self, mock_perf_counter_ns):
        """No error must be raised if time delta is zero."""
        mock_perf_counter_ns.side_effect = [0, 0]
        with CodeTimer() as ct:
            pass
        # Test passes if no exceptions are raised

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
        for time_ns in [
            int("".join(str(x % 10) for x in range(mx))) for mx in range(2, 22)
        ]:
            # [1, 12, 123, ... 12345678901234567890]
            for min_digits in range(1, 25):
                with self.subTest(time_ns=time_ns, min_digits=min_digits):
                    digit_count = sum(
                        c.isdigit() for c in CodeTimer._format_time(time_ns, min_digits)
                    )
                    self.assertGreaterEqual(digit_count, min_digits)

    def test__format_time(self):
        """Tests that time formatting works as expected."""
        self.assertEqual(
            CodeTimer._format_time(1, 3),
            "1.00 ns",
        )
        self.assertEqual(
            CodeTimer._format_time(NS_PER_MICROSECOND, 3),
            "1.00 us",
        )
        self.assertEqual(
            CodeTimer._format_time(NS_PER_MILLISECOND, 3),
            "1.00 ms",
        )
        self.assertEqual(
            CodeTimer._format_time(NS_PER_SECOND, 3),
            "1.00 s",
        )
        self.assertEqual(
            CodeTimer._format_time(NS_PER_MINUTE - NS_PER_MILLISECOND, 7),
            "59.99900 s",
        )
        self.assertEqual(
            CodeTimer._format_time(NS_PER_MINUTE, 7),
            "01:00.0000",
        )
        self.assertEqual(
            CodeTimer._format_time(NS_PER_HOUR, 7),
            "01:00:00.00",
        )
        self.assertEqual(
            CodeTimer._format_time(NS_PER_DAY, 7),
            "1 day, 00:00:00",
        )
        self.assertEqual(
            CodeTimer._format_time(2 * NS_PER_DAY, 7),
            "2 days, 00:00:00",
        )
        self.assertEqual(
            CodeTimer._format_time(12345678901234567890, 25),
            "142,889 days, 19:15:01.2345678900000",
        )

    @mock.patch("builtins.print")
    def test_properties(self, mock_print: mock.MagicMock):
        """Tests 'message' and 'time_str' properties."""
        # Test default values, if called before the measurement
        ct = CodeTimer()
        self.assertEqual(ct.message, "No code execution has taken place yet.")
        self.assertEqual(ct.time_str, "")
        # Test values after measurement correspond to the printout
        with ct:
            pass
        self.assertEqual(ct.message, mock_print.call_args.args[0])
        self.assertEqual(ct.time_str, re.search("took (.*)\.", ct.message).group(1))

    @mock.patch("builtins.print")
    def test_decorator(self, mock_print: mock.MagicMock):
        """Tests that the class can be used as a decorator."""

        @CodeTimer()
        def func():
            return 123

        self.assertEqual(func(), 123)
        mock_print.assert_called_once()
        self.assertIn("Code execution", mock_print.call_args.args[0])

    @flaky
    def test_results_collection(self):
        """Tests storing the benchmark results into a user-provided list."""
        results = []

        @CodeTimer(no_print=True, results=results)
        def sleep_ms(ms: int):
            sleep(ms / 1000)

        sleep_times = [10, 20, 30]
        for idx, t_sleep in enumerate(sleep_times):
            sleep_ms(t_sleep)
        for idx, t_sleep in enumerate(sleep_times):
            self.assertAlmostEqual(results[idx].ms, t_sleep, delta=2)


if __name__ == "__main__":
    unittest.main()
