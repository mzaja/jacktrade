import unittest

from jacktrade import cached_method


class CachedClass:
    """Test fixture class with cached class and instance methods."""

    class_call_count = 0

    def __init__(self):
        self.call_count = 0

    @cached_method
    def instance_method(self, a=0, b=0, c=0) -> int:
        self.call_count += 1
        return a + 2 * b + 3 * c

    @classmethod
    @cached_method
    def class_method(cls, a=0, b=0, c=0) -> int:
        cls.class_call_count += 1
        return a + 2 * b + 3 * c


class CachedMethodTest(unittest.TestCase):
    """Tests for the cached_method decorator."""

    def test_instance_method(self):
        """Caching an instance method."""
        obj = CachedClass()
        self.assertEqual(obj.call_count, 0)

        # New calls
        self.assertEqual(obj.instance_method(), 0)
        self.assertEqual(obj.call_count, 1)

        self.assertEqual(obj.instance_method(1, 2, 3), 14)
        self.assertEqual(obj.call_count, 2)

        self.assertEqual(obj.instance_method(4, 5, 6), 32)
        self.assertEqual(obj.call_count, 3)

        # Repeated calls
        self.assertEqual(obj.instance_method(), 0)
        self.assertEqual(obj.call_count, 3)

        self.assertEqual(obj.instance_method(1, 2, 3), 14)
        self.assertEqual(obj.call_count, 3)

        self.assertEqual(obj.instance_method(4, 5, 6), 32)
        self.assertEqual(obj.call_count, 3)

        # Functionally an existing call, but with a different argument mix
        self.assertEqual(obj.instance_method(1, 2, c=3), 14)
        self.assertEqual(obj.call_count, 4)

        # Functionally an existing call, but with a different argument mix
        self.assertEqual(obj.instance_method(a=1, b=2, c=3), 14)
        self.assertEqual(obj.call_count, 5)

        # Shuffling the order of keyword arguments does not make a difference
        self.assertEqual(obj.instance_method(c=3, b=2, a=1), 14)
        self.assertEqual(obj.call_count, 5)

    def test_class_method(self):
        """Caching a class method."""
        obj = CachedClass
        self.assertEqual(obj.class_call_count, 0)

        # New calls
        self.assertEqual(obj.class_method(), 0)
        self.assertEqual(obj.class_call_count, 1)

        self.assertEqual(obj.class_method(1, 2, 3), 14)
        self.assertEqual(obj.class_call_count, 2)

        self.assertEqual(obj.class_method(4, 5, 6), 32)
        self.assertEqual(obj.class_call_count, 3)

        # Repeated calls
        self.assertEqual(obj.class_method(), 0)
        self.assertEqual(obj.class_call_count, 3)

        self.assertEqual(obj.class_method(1, 2, 3), 14)
        self.assertEqual(obj.class_call_count, 3)

        self.assertEqual(obj.class_method(4, 5, 6), 32)
        self.assertEqual(obj.class_call_count, 3)

        # Functionally an existing call, but with a different argument mix
        self.assertEqual(obj.class_method(1, 2, c=3), 14)
        self.assertEqual(obj.class_call_count, 4)

        # Functionally an existing call, but with a different argument mix
        self.assertEqual(obj.class_method(a=1, b=2, c=3), 14)
        self.assertEqual(obj.class_call_count, 5)

        # Shuffling the order of keyword arguments should not make a difference
        self.assertEqual(obj.class_method(c=3, b=2, a=1), 14)
        self.assertEqual(obj.class_call_count, 5)


if __name__ == "__main__":
    unittest.main()
