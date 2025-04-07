import csv
import glob
import os
from argparse import ArgumentParser


# ---------------------------------------------------------------------------
# FUNCTIONS
# ---------------------------------------------------------------------------
def merge_csv_files(
    src_files: list[str], dest_file: str, has_headers: bool = True
) -> str | None:
    """
    Merges multiple CSV files into a single one.
    Parameters:
        - src_files: A list of paths to source files to combine.
        - dest_file: Path to the output file.
        - has_headers:
            If True (default), the first row of each CSV files is treated as a header
            and is written to the output file only once. The files must have the identical
            number of columns and column names, but not necessarily in the same order.
            If False, CSV files' contents are concatenated in full to one another.

    Returns:
        - Path to the output file if the file has been created.
        - None if the output file nas not been created.
    """
    if not src_files:
        return None  # Don't even create a new file if there are no sources
    with open(dest_file, "w", newline="") as fd:
        if has_headers:
            # Peak into the first file to obtain headers
            with open(src_files[0], "r") as fs:
                reader = csv.DictReader(fs)
                column_names = reader.fieldnames
            # Initialise the writer with headers
            writer = csv.DictWriter(fd, column_names)
            writer.writeheader()
        else:
            writer = csv.writer(fd)
        # Iterate over the files and write their contents into dest
        for src_file in src_files:
            with open(src_file, "r") as fs:
                reader_type = csv.DictReader if has_headers else csv.reader
                writer.writerows(reader_type(fs))
    return dest_file


# ---------------------------------------------------------------------------
# COMMAND LINE UTILITY
# ---------------------------------------------------------------------------
def _create_parser() -> ArgumentParser:
    """Creates and returns a command line argument parser."""
    parser = ArgumentParser(prog="merge", description="File merging utility")
    subparsers = parser.add_subparsers(
        title="file types", dest="file_type", required=True
    )
    parser_csv = subparsers.add_parser(
        "csv",
        description=(
            "Merge CSV files into one. Automatically removes headers from the 2nd file onwards."
        ),
        help="Comma Separated Values",
    )
    parser_csv.add_argument(
        "dest_file", metavar="DEST_FILE", help="Destination CSV file."
    )
    parser_csv.add_argument(
        "src_files",
        metavar="SRC_FILES",
        help=(
            "Source CSV files. Can be paths to multiple CSV files, glob patterns or directories. "
            "If a directory is provided, merges all CSV files in that directory, excluding sub-directories."
        ),
        nargs="+",
    )
    parser_csv.add_argument(
        "-g",
        "--glob",
        action="store_true",
        help="Treat SRC_FILES as glob patterns.",
    )
    parser_csv.add_argument(
        "-nh",
        "--no-headers",
        action="store_false",
        dest="has_headers",
        help="Preserve the first row of each CSV file by treating it as data instead of a header.",
    )
    return parser


def _merge_files_cli_app() -> None:
    """Command line application for merging files."""
    parser = _create_parser()
    args = parser.parse_args()
    match args.file_type:
        case "csv":
            src_files = []
            if args.glob:
                for pattern in args.src_files:
                    # Globbed files must be sorted, else their order is random
                    src_files += sorted(glob.glob(pattern))
            else:
                for src_path in args.src_files:
                    if os.path.isdir(src_path):
                        # Globbed files must be sorted, else their order is random
                        src_files += sorted(glob.glob(os.path.join(src_path, "*.csv")))
                    else:
                        src_files.append(src_path)

            merge_csv_files(src_files, args.dest_file, args.has_headers)
