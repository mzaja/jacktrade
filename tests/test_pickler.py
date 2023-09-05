import os.path
import tempfile
import unittest

from jacktrade import pickle_object, unpickle_object


class PickerTest(unittest.TestCase):
    """
    Tests the convenience pickling functions.
    """

    def test_pickle_unpickle(self):
        """Tests pickling and unpickling an object."""
        with tempfile.TemporaryDirectory() as td:
            obj = [1, 2, 3]
            filename = os.path.join(td, "obj.pickle")
            pickle_object(obj, filename)
            self.assertEqual(unpickle_object(filename), obj)


if __name__ == "__main__":
    unittest.main()
