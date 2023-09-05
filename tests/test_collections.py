import unittest
from dataclasses import dataclass
from typing import Iterator

from jacktrade import (
    BaseMapping,
    chunkify,
    flatten_dict,
    flatten_list,
    get_first_dict_item,
    get_first_dict_key,
    get_first_dict_value,
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


@dataclass
class Person:
    """For testing BaseMapping."""

    name: str
    age: int
    alive: bool


PEOPLE = (
    Person("John Doe", 27, True),
    Person("Jane Doe", 39, True),
    Person("David Hume", 313, False),
)

CORRUPT_PEOPLE = (Person("Zargothrax", "666", None), None)


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


class BaseMappingTest(unittest.TestCase):
    """
    Tests BaseMapping class.
    """

    @staticmethod
    def first_name_getter(person: Person) -> str:
        return person.name.split(" ")[0]

    @staticmethod
    def age_getter(person: Person) -> int:
        return person.age

    @staticmethod
    def is_alive(person: Person) -> bool:
        return person.alive is True

    @staticmethod
    def is_less_than_30(person: Person) -> bool:
        return person.age < 30

    def test_basic_mapping(self):
        """Tests basic mapping with key and value getters."""
        mapping = BaseMapping(PEOPLE, self.first_name_getter, self.age_getter)
        expected_result = {"John": 27, "Jane": 39, "David": 313}
        self.assertEqual(mapping, expected_result)

    def test_with_condition(self):
        """Tests mapping with a condition function provided."""
        mapping = BaseMapping(
            PEOPLE, self.first_name_getter, self.age_getter, self.is_less_than_30
        )
        expected_result = {"John": 27}
        self.assertEqual(mapping, expected_result)
        mapping = BaseMapping(
            PEOPLE, self.first_name_getter, self.age_getter, self.is_alive
        )
        expected_result = {"John": 27, "Jane": 39}
        self.assertEqual(mapping, expected_result)

    def test_skip_exceptions(self):
        """Tests discarding elements which trigger an exception."""
        mapping = BaseMapping(
            PEOPLE + CORRUPT_PEOPLE,
            self.first_name_getter,
            self.age_getter,
            self.is_less_than_30,
            skip_exceptions=(TypeError, AttributeError),
        )
        expected_result = {"John": 27}
        self.assertEqual(mapping, expected_result)

    def test_raise_exceptions(self):
        """Exception is raised because not all errors are handled."""
        # Skip no exceptions
        with self.assertRaises(TypeError):
            mapping = BaseMapping(
                PEOPLE + CORRUPT_PEOPLE,
                self.first_name_getter,  # Raises AttributeError (2nd)
                self.age_getter,
                self.is_less_than_30,  # Raises TypeError (1st)
            )
        # Skip first exception but not the second one
        with self.assertRaises(AttributeError):
            mapping = BaseMapping(
                PEOPLE + CORRUPT_PEOPLE,
                self.first_name_getter,  # Raises AttributeError (2nd)
                self.age_getter,
                self.is_less_than_30,  # Raises TypeError (1st)
                skip_exceptions=(TypeError,),
            )

    def test_repr(self):
        """Tests that __repr__ magic method displays the name of the derived class."""

        class DerivedMapping(BaseMapping):
            def __init__(self, items):
                # This is not how one would usually use a class
                super().__init__(items, lambda x: x[0], lambda x: x[1])

        mapping = repr(DerivedMapping([("Will", 29)]))
        # Derived class name is displated first
        self.assertTrue(mapping.startswith("DerivedMapping"))
        # Contents are also displayed, like in a normal dict
        self.assertIn(repr({"Will": 29}), mapping)


if __name__ == "__main__":
    unittest.main()
