import time


# ---------------------------------------------------------------------------
# CLASSES
# ---------------------------------------------------------------------------
class CodeTimer:
    """
    Times a section of code inside a "with" statement.

    Example usage:
        with CodeTimer() as t:
            # Code to time
        print(f"Execution took {t.s} seconds / {t.ms} milliseconds / {t.us} microseconds / {t.ns} nanoseconds.")

    Parameters:
        - no_print: If True, no message will be printed on exiting the timing block.
        - min_digits: Minimal number of digits to display when printing the result.

    Attributes:
        - ns: Code execution time in nanoseconds.
        - us: Code execution time in microseconds.
        - ms: Code execution time in milliseconds.
        - s: Code execution time in seconds.
    """

    UNITS = ("ns", "us", "ms", "s")

    def __init__(self, no_print: bool = False, min_digits: int = 3):
        self._no_print = no_print
        self._min_digits = min_digits
        self.ns = -1
        self.us = -1
        self.ms = -1
        self.s = -1

    def __enter__(self):
        self.start = time.perf_counter_ns()
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.ns = time.perf_counter_ns() - self.start
        self.us = self.ns / 1e3
        self.ms = self.ns / 1e6
        self.s = self.ns / 1e9
        if not self._no_print:
            print(
                f"Code execution took {self._format_time(self.ns, self._min_digits)}."
            )

    @classmethod
    def _format_time(cls, time_ns: int, min_digits: int) -> str:
        """Automatically selects the suitable time unit and returns a formatted string."""
        n_digits = len(str(time_ns))
        n_divisions = min(
            (n_digits - 1) // 3, len(cls.UNITS) - 1
        )  # How many times to divide by 1000
        digits_after_division = n_digits - 3 * n_divisions
        decimal_places = max(0, min_digits - digits_after_division)
        fmt = (
            ",." + str(decimal_places) + "f"
        )  # How many digits spill over behind the decimal place
        return f"{time_ns / (1000 ** n_divisions):{fmt}} {cls.UNITS[n_divisions]}"
