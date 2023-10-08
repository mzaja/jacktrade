import unittest
from dataclasses import dataclass
from typing import Iterator

from jacktrade import (
    BaseMapping,
    MasterDict,
    Permutations,
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

    def test_permutations(self):
        """Tests Permutations class."""
        kwargs_in = {"n": [1, 2, 3], "c": ["A", "B"]}
        perms = Permutations(**kwargs_in)
        kwargs_out = [
            {"n": 1, "c": "A"},
            {"n": 1, "c": "B"},
            {"n": 2, "c": "A"},
            {"n": 2, "c": "B"},
            {"n": 3, "c": "A"},
            {"n": 3, "c": "B"},
        ]
        self.assertEqual(len(perms), 6)
        self.assertEqual(
            perms.args, [(1, "A"), (1, "B"), (2, "A"), (2, "B"), (3, "A"), (3, "B")]
        )
        self.assertEqual(perms.kwargs, kwargs_out)
        self.assertEqual(list(perms), kwargs_out)  # Tests __iter__
        self.assertIn(str(kwargs_in), str(perms))  # Tests __repr__
        self.assertIn(perms.__class__.__name__, str(perms))  # Tests __repr__


class MasterDictTest(unittest.TestCase):
    """
    Tests MasteDict class.
    """

    def setUp(self) -> None:
        self.master = MasterDict(
            letters={1: "A", 2: "B"}, numbers={1: "1", 2: "2", 3: "3"}
        )

    def test_delete_keys(self):
        """Tests deleting individual keys from a collection of dicts."""
        self.master.delete_keys(1, 3)
        self.assertEqual(self.master.letters, {2: "B"})  # Deleted: 1
        self.assertEqual(self.master.numbers, {2: "2"})  # Deleted: 1, 3

    def test_clear_all(self):
        """Tests clearing all sub-dicts."""
        self.master.clear_all()
        self.assertEqual(self.master.letters, {})
        self.assertEqual(self.master.numbers, {})

    def test_as_dict(self):
        """Tests converting a MasterDict instance to a dict."""
        self.assertEqual(
            self.master.as_dict(),
            {"letters": {1: "A", 2: "B"}, "numbers": {1: "1", 2: "2", 3: "3"}},
        )

    def test_str_and_repr(self):
        """Tests string representations of a MasterDict object."""
        display = (
            "MasterDict(letters={1: 'A', 2: 'B'}, numbers={1: '1', 2: '2', 3: '3'})"
        )
        self.assertEqual(repr(self.master), display)
        self.assertEqual(str(self.master), display)


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

    def test_invert(self):
        """Tests inverting the mapping."""
        mapping = BaseMapping([(1, "a"), (2, "b")], lambda x: x[0], lambda x: x[1])
        self.assertEqual(mapping.invert(), {"a": 1, "b": 2})

    def test_invert_strict_mode(self):
        """Tests strict mode when inverting the mapping."""
        mapping = BaseMapping([(1, "a"), (2, "a")], lambda x: x[0], lambda x: x[1])
        self.assertEqual(len(mapping.invert(strict=False)), 1)
        with self.assertRaises(ValueError):
            mapping.invert(strict=True)

    def test__invert_and_cast(self):
        """Tests inverting the mapping and casting it to another mapping type."""
        first_name_getter = self.first_name_getter
        age_getter = self.age_getter

        class NameToAge(BaseMapping):
            def __init__(self, items):
                super().__init__(items, first_name_getter, age_getter)

            def invert(self, strict: bool = False) -> "AgeToName":
                return super()._invert_and_cast(AgeToName, strict)

        class AgeToName(BaseMapping):
            def __init__(self, items):
                super().__init__(items, age_getter, first_name_getter)

            def invert(self, strict: bool = False) -> NameToAge:
                return self._invert_and_cast(NameToAge, strict)

        mapping = AgeToName(PEOPLE)
        inverse_mapping = mapping.invert()
        self.assertIsInstance(inverse_mapping, NameToAge)
        self.assertEqual(mapping, inverse_mapping.invert())

    def test__invert_and_cast_to_generic_type(self):
        """Tests inverting the mapping and casting it to a generic dict type."""
        first_name_getter = self.first_name_getter
        age_getter = self.age_getter

        class AgeToName(BaseMapping):
            def __init__(self, items):
                super().__init__(items, age_getter, first_name_getter)

            def invert(self, strict: bool = False) -> dict:
                return self._invert_and_cast(dict, strict)

        mapping = AgeToName(PEOPLE)
        inverse_mapping = mapping.invert()
        self.assertEqual(type(inverse_mapping), dict)
        self.assertEqual(mapping, BaseMapping.invert(inverse_mapping))


if __name__ == "__main__":
    unittest.main()
