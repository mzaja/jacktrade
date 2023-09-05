from collections import defaultdict, deque
from pathlib import Path
from typing import Iterator


# ---------------------------------------------------------------------------
# CLASSES
# ---------------------------------------------------------------------------
class StringBuffers:
    """
    Sorts, stores and flushes string data to a disk. The main purpose
    of this buffer is to reduce the number of file open/close cycles
    and speed up logging of string data to disk.
    """

    def __init__(self, output_dir: str = ".", buffer_size: int = None):
        self._output_dir = Path(output_dir)
        self._output_dir.mkdir(parents=True, exist_ok=True)
        self._buffer_size = buffer_size
        self._buffers = defaultdict(lambda sz=buffer_size: deque(maxlen=sz))

    def _flush_buffer(self, output_file: str, buffer: deque) -> str:
        """
        Flushes the buffer to the output file.
        Moved to a separate function for DRY, and so that flush_all could
        iterate over the dict more efficiently.
        Returns the full path to the file to which the data was flushed.
        """
        output_file_path = self._output_dir / output_file
        try:
            # Try getting the first item. If there isn't one,
            # no point to even open the file.
            first_item = buffer.popleft()
            with open(output_file_path, "a") as f:
                f.write(first_item)
                while True:
                    f.write(buffer.popleft())
        except IndexError:
            pass  # When the buffer is empty, flushing is done
        return str(output_file_path)

    def add(self, output_file: str, data: str) -> int:
        """
        Adds the data to the buffer for the specified output file.
        Returns the number of elements in the buffer after the addition.
        If the addition causes the buffer to reach its capacity, the buffer
        is automatically flushed to the disk.
        """
        (buffer := self._buffers[output_file]).append(data)
        if self._buffer_size and (len(buffer) >= self._buffer_size):
            self._flush_buffer(output_file, buffer)
        return len(buffer)

    def flush(self, output_file: str) -> str:
        """
        Flushes the data in output file's buffer to the output file.
        Returns the full path to the file to which the data was flushed.
        """
        return self._flush_buffer(output_file, self._buffers[output_file])

    def flush_all(self) -> None:
        """Flushes all buffers to disk."""
        for output_file, buffer in self._buffers.items():
            self._flush_buffer(output_file, buffer)

    def remove(self, output_file: str) -> str:
        """
        Removes the output file from the buffer,
        flushing data to disk if it is not empty.
        Returns the full path to the file to which the data was flushed.
        """
        output_file_path = self.flush(output_file)
        del self._buffers[output_file]
        return output_file_path

    @property
    def files(self) -> list[str]:
        """
        Returns a list of output files bound to string buffers.
        """
        return list(self._buffers.keys())

    def __iter__(self) -> Iterator[tuple]:
        return iter(self._buffers.items())
