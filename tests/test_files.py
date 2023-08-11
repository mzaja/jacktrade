import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from jacktrade import merge_csv_files


class MergeCsvFilesTest(unittest.TestCase):
    """
    Tests merge_csv_files() function.

    NOTE: The behaviour of the function when has_headers=True but the source CSV
          files have mismatching headers is underfined and therefeore not tested.
    """

    SRC_FILES = ("tests/test_data/names_1.csv", "tests/test_data/names_2.csv")

    def setUp(self):
        self.tempdir = TemporaryDirectory()
        self.dest_file = str(Path(self.tempdir.name) / "merged.csv")

    def tearDown(self):
        self.tempdir.cleanup()

    def assert_file_contents_equal(self, file: str, contents: str) -> str:
        """Asserts that the file contains the provided text."""
        with open(file, "r") as f:
            self.assertEqual(f.read(), contents)

    def test_merge_has_headers(self):
        """Merge files considering the headers."""
        dest_file = merge_csv_files(
            self.SRC_FILES,
            self.dest_file,
            has_headers=True,
        )
        self.assert_file_contents_equal(
            dest_file,
            "NAME,SURNAME,AGE\nDon,Johnson,52\nWilliam,Andrews,27\nAdam,Smith,73\n",
        )

    def test_merge_no_headers(self):
        """Merge files' content verbatim when data is declared as not having headers."""
        dest_file = merge_csv_files(
            self.SRC_FILES,
            self.dest_file,
            has_headers=False,
        )
        self.assert_file_contents_equal(
            dest_file,
            "NAME,SURNAME,AGE\nDon,Johnson,52\nWilliam,Andrews,27\nAGE,SURNAME,NAME\n73,Smith,Adam\n",
        )

    def test_no_files_provided(self):
        """Function returns None when no merging took place."""
        self.assertIsNone(merge_csv_files([], self.dest_file))


if __name__ == "__main__":
    unittest.main()
