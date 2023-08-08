import unittest
from typing import Iterator

from jacktrade import (
    flatten_dict,
    get_first_dict_item,
    get_first_dict_key,
    get_first_dict_value,
    flatten_list,
    chunkify,
    ichunkify,
    limit_iterator,
)

# ---------------------------------------------------------------------------
# TEST FIXTURES
# ---------------------------------------------------------------------------
MULTILEVEL_DICT = {"a1": {"a2": {"a3": 1, "b3": 2}, "b2": 3}, "b1": 4, "c1": 5}
MULTILEVEL_LIST = [[[1, 2], 3], 4, 5]
LONG_LIST = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
CHUNKIFY_TEST_PARAMS = [
    # Parameters are (chunk size, first element, last element, element count)
    (1, [1], [20], 20),
    (3, [1, 2, 3], [19, 20], 7),
    (5, [1, 2, 3, 4, 5], [16, 17, 18, 19, 20], 4),
    (99, LONG_LIST, LONG_LIST, 1),
]


# ---------------------------------------------------------------------------
# TEST CASES
# ---------------------------------------------------------------------------
class CollectionsTest(unittest.TestCase):
    """
    Tests the collections submodule.
    """

    def test_flatten_dict_core(self):
        """Tests flattenning a multilevel dict."""
        input_data = MULTILEVEL_DICT
        self.assertEqual(flatten_dict(input_data), [1, 2, 3, 4, 5])

    def test_flatten_dict_max_depth(self):
        """Tests flattening a multilevel dict when max_depth is reached."""
        input_data = MULTILEVEL_DICT
        self.assertEqual(
            flatten_dict(input_data, max_depth=2), [{"a3": 1, "b3": 2}, 3, 4, 5]
        )

    def test_get_first_dict_x(self):
        """Tests the get_first_dict_* functions."""
        test_dict = {"a": 1, "b": 2, "c": 3}
        self.assertEqual(get_first_dict_item(test_dict), ("a", 1))
        self.assertEqual(get_first_dict_key(test_dict), "a")
        self.assertEqual(get_first_dict_value(test_dict), 1)

    def test_flatten_list_core(self):
        """Tests flattening a multilevel list."""
        input_data = MULTILEVEL_LIST
        self.assertEqual(flatten_list(input_data), [1, 2, 3, 4, 5])

    def test_flatten_list_max_depth(self):
        """Tests flattening a multilevel list."""
        input_data = MULTILEVEL_LIST
        self.assertEqual(flatten_list(input_data, max_depth=2), [[1, 2], 3, 4, 5])

    def test_chunkify(self):
        """Tests chunkify function."""
        for chunk_size, first_exp, last_exp, count_exp in CHUNKIFY_TEST_PARAMS:
            with self.subTest(chunk_size=chunk_size):
                chunks = list(chunkify(LONG_LIST, chunk_size))
                self.assertEqual(first_exp, chunks[0])
                self.assertEqual(last_exp, chunks[-1])
                self.assertEqual(count_exp, len(chunks))

    def test_chunkify_infinite_chunk_size(self):
        """Tests chunkify when chunk_size is not specified, making it infinite."""
        self.assertEqual(list(chunkify(LONG_LIST, None)), [LONG_LIST])

    def test_ichunkify(self):
        """Tests ichunkify function."""
        for chunk_size, first_exp, last_exp, count_exp in CHUNKIFY_TEST_PARAMS:
            with self.subTest(chunk_size=chunk_size):
                # Chunks must be consumed as they are yielded
                for chunk_count, chunk in enumerate(
                    ichunkify(LONG_LIST, chunk_size), 1
                ):
                    self.assertIsInstance(chunk, Iterator)
                    chunk = list(chunk)  # Consume the chunk
                    if chunk_count == 1:
                        first_chunk = chunk
                last_chunk = chunk
                self.assertEqual(first_exp, first_chunk)
                self.assertEqual(last_exp, last_chunk)
                self.assertEqual(count_exp, chunk_count)

    def test_ichunkify_infinite_chunk_size(self):
        """Tests ichunkify when chunk_size is not specified, making it infinite."""
        self.assertEqual(list(next(ichunkify(LONG_LIST, None))), LONG_LIST)

    def test_limited_iterator(self):
        """Tests limiting the iterator to max elements."""
        self.assertEqual(list(limit_iterator(LONG_LIST, 5)), [1, 2, 3, 4, 5])
        self.assertEqual(list(limit_iterator(iter(LONG_LIST), 5)), [1, 2, 3, 4, 5])
        self.assertEqual(list(limit_iterator(LONG_LIST, 99)), LONG_LIST)
        self.assertEqual(list(limit_iterator(iter(LONG_LIST), 99)), LONG_LIST)


if __name__ == "__main__":
    unittest.main()
