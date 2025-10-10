import unittest

from jacktrade import cached_method


class CachedClass:
    """Test fixture class with cached class and instance methods."""

    class_call_count = 0

    def __init__(self):
        self.call_count = 0

    @cached_method
    def instance_method(self, single=0, double=0, triple=0) -> int:
        self.call_count += 1
        return single + 2 * double + 3 * triple

    @classmethod
    @cached_method
    def class_method(cls, single=0, double=0, triple=0) -> int:
        cls.class_call_count += 1
        return single + 2 * double + 3 * triple


class CachedMethodTest(unittest.TestCase):
    """Tests for the cached_method decorator."""

    # Data implementing different test sub-cases:
    # args, kwargs, result, cache_miss
    FIXTURES = (
        # New calls -> cache miss
        ((), {}, 0, True),
        ((1, 2), {}, 5, True),
        ((1, 2, 3), {}, 14, True),
        ((4, 5, 6), {}, 32, True),
        # Repeated calls -> cache hit
        ((), {}, 0, False),
        ((1, 2), {}, 5, False),
        ((1, 2, 3), {}, 14, False),
        ((4, 5, 6), {}, 32, False),
        # Repeated calls with a different argument mix -> cache hit
        # Same as (0, 0, 0)
        ((0,), {}, 0, False),
        ((0, 0, 0), {}, 0, False),
        ((), {"single": 0, "double": 0}, 0, False),
        # Same as (1, 2, 0)
        ((1, 2, 0), {}, 5, False),
        ((1,), {"double": 2}, 5, False),
        ((), {"single": 1, "double": 2}, 5, False),
        # Same as (1, 2, 3)
        ((), {"single": 1, "double": 2, "triple": 3}, 14, False),
        ((), {"triple": 3, "double": 2, "single": 1}, 14, False),
    )

    def test_instance_method(self):
        """Caching an instance method."""
        obj = CachedClass()
        call_count = 0
        self.assertEqual(obj.call_count, call_count)

        for args, kwargs, result, cache_miss in self.FIXTURES:
            self.assertEqual(obj.instance_method(*args, **kwargs), result)
            call_count += 1 if cache_miss else 0
            self.assertEqual(obj.call_count, call_count)

    def test_class_method(self):
        """Caching a class method."""
        obj = CachedClass
        call_count = 0
        self.assertEqual(obj.class_call_count, call_count)

        for args, kwargs, result, cache_miss in self.FIXTURES:
            self.assertEqual(obj.class_method(*args, **kwargs), result)
            call_count += 1 if cache_miss else 0
            self.assertEqual(obj.class_call_count, call_count)


if __name__ == "__main__":
    unittest.main()
