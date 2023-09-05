import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from jacktrade import StringBuffers

FILE_1 = "abc.txt"
FILE_2 = "def.txt"
TEST_DATA = [
    (FILE_1, "1"),
    (FILE_2, "2"),
    (FILE_1, "3"),
    (FILE_1, "4"),
]  # FILE_1: "134", FILE_2: "2"


class StringBuffersTest(unittest.TestCase):
    """
    Tests the StringBuffers class.
    """

    def setUp(self) -> None:
        self.tempdir = TemporaryDirectory()
        self.file_1_path = Path(self.tempdir.name) / FILE_1
        self.file_2_path = Path(self.tempdir.name) / FILE_2

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def load_data(self, buffers: StringBuffers) -> StringBuffers:
        """Loads data for test cases."""
        for args in TEST_DATA:
            buffers.add(*args)
        return buffers

    def assert_in_file(self, file_path: str, file_content: str):
        """Checks the file's contents."""
        with open(file_path) as f:
            self.assertEqual(f.read(), file_content)

    def test_auto_flush(self):
        """Tests that buffer_size can be None."""
        self.load_data(StringBuffers(self.tempdir.name, buffer_size=2))
        self.assert_in_file(self.file_1_path, "13")
        self.assertFalse(self.file_2_path.exists())

    def test_flush(self):
        buffers = self.load_data(StringBuffers(self.tempdir.name))
        self.assertFalse(self.file_1_path.exists())
        self.assertFalse(self.file_2_path.exists())
        buffers.flush(FILE_1)
        self.assert_in_file(self.file_1_path, "134")
        self.assertFalse(self.file_2_path.exists())
        self.assertEqual(buffers.files, [FILE_1, FILE_2])

    def test_flush_all(self):
        buffers = self.load_data(StringBuffers(self.tempdir.name))
        self.assertFalse(self.file_1_path.exists())
        self.assertFalse(self.file_2_path.exists())
        buffers.flush_all()
        self.assert_in_file(self.file_1_path, "134")
        self.assert_in_file(self.file_2_path, "2")
        self.assertEqual(buffers.files, [FILE_1, FILE_2])

    def test_remove(self):
        buffers = self.load_data(StringBuffers(self.tempdir.name))
        self.assertEqual(buffers.files, [FILE_1, FILE_2])
        self.assertFalse(self.file_1_path.exists())
        self.assertFalse(self.file_2_path.exists())
        # Dump and remove file 1
        buffers.remove(FILE_1)
        self.assert_in_file(self.file_1_path, "134")
        self.assertFalse(self.file_2_path.exists())  # File 2 has not been dumped yet
        self.assertEqual(buffers.files, [FILE_2])
        # Dumpr and remove file 2
        buffers.remove(FILE_2)
        self.assert_in_file(self.file_2_path, "2")
        self.assertEqual(buffers.files, [])

    def test_files_property(self):
        buffers = self.load_data(StringBuffers(self.tempdir.name))
        self.assertEqual(buffers.files, [FILE_1, FILE_2])

    def test_iter(self):
        buffers = self.load_data(StringBuffers(self.tempdir.name))
        iterable = list(buffers)
        self.assertEqual(iterable[0][0], FILE_1)
        self.assertEqual(list(iterable[0][1]), ["1", "3", "4"])
        self.assertEqual(iterable[1][0], FILE_2)
        self.assertEqual(list(iterable[1][1]), ["2"])


if __name__ == "__main__":
    unittest.main()
