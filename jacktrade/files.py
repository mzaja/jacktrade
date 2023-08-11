import csv


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
