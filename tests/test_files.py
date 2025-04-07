import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock

from jacktrade import merge_csv_files
from jacktrade.files import _merge_files_cli_app


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


class MergeFilesCLITest(unittest.TestCase):
    """Tests the command line utility for merging files."""

    TEST_DATA_DIR = Path("tests/test_data")
    SRC_FILES = sorted(str(f) for f in TEST_DATA_DIR.glob("*.csv"))

    def setUp(self):
        self.sys_argv_old = sys.argv

    def tearDown(self):
        sys.argv = self.sys_argv_old

    @staticmethod
    def call_merge_csv_with_args(*args) -> mock._Call:
        """
        Calls merge csv [args] command line utility. Returns the call arguments
        provided
        """
        with mock.patch("jacktrade.files.merge_csv_files") as mock_merge_csv_files:
            sys.argv = ["merge", "csv"] + list(args)
            _merge_files_cli_app()
            return mock_merge_csv_files.call_args

    def test_merge_csv_files_list_of_files(self):
        """Tests calling merge csv with a list of files."""
        call_args = self.call_merge_csv_with_args("dest.csv", "src1.csv", "src2.csv")
        self.assertEqual(call_args.args, (["src1.csv", "src2.csv"], "dest.csv", True))

    def test_merge_csv_files_list_of_nonexistent_directories(self):
        """
        Tests calling merge csv with a list of nonexistent directories,
        which end up being treated as ordinary files.
        """
        call_args = self.call_merge_csv_with_args("dest.csv", "dir1", "dir2")
        self.assertEqual(call_args.args, (["dir1", "dir2"], "dest.csv", True))

    def test_merge_csv_files_list_of_valid_directories(self):
        """
        Tests calling merge csv with a list of existing directories containing CSV files.
        """
        call_args = self.call_merge_csv_with_args("dest.csv", str(self.TEST_DATA_DIR))
        self.assertEqual(call_args.args, (self.SRC_FILES, "dest.csv", True))

    def test_merge_csv_files_list_directories_not_recursive(self):
        """
        Tests that calling merge csv with a list of directories is
        not recursive in its search for files.
        """
        call_args = self.call_merge_csv_with_args(
            "dest.csv", str(self.TEST_DATA_DIR.parent)
        )
        self.assertEqual(call_args.args, ([], "dest.csv", True))

    def test_merge_csv_files_list_of_glob_patterns(self):
        """Tests calling merge csv with a list of glob patterns."""
        for option in ["-g", "--glob"]:
            for patterns in [
                ("tests/**/*.csv",),  # Recursive
                ("tests/test_data/*.csv",),  # Non-recursive
                ("tests/**/*1.csv", "tests/**/*2.csv"),  # Patterns stack
            ]:
                call_args = self.call_merge_csv_with_args(option, "dest.csv", *patterns)
                self.assertEqual(call_args.args, (mock.ANY, "dest.csv", True))
                # src_files have a mixed of use of back and forward slashes depending on the
                # platform, which are appended to the original glob pattern using forward slashes.
                # The patterns need to be normalised by conveting them to Path objects
                # first and then back to strings.
                called_with_files = call_args.args[0]
                self.assertEqual(
                    [str(Path(f)) for f in called_with_files], self.SRC_FILES
                )

            # Call with a pattern not matching any files
            call_args = self.call_merge_csv_with_args(
                option, "dest.csv", "*tests/test_data/*.in"
            )
            self.assertEqual(call_args.args, ([], "dest.csv", True))

    def test_merge_csv_files_no_headers(self):
        """Tests calling merge csv with a -nh/--no-headers option."""
        for option in ["-nh", "--no-headers"]:
            call_args = self.call_merge_csv_with_args(option, "dest.csv", "src.csv")
            self.assertEqual(call_args.args, (["src.csv"], "dest.csv", False))


if __name__ == "__main__":
    unittest.main()
