from __future__ import annotations

import pytest
from coola import objects_are_equal

from votingsys.utils.mapping import find_max_in_mapping

#########################################
#     Tests for find_max_in_mapping     #
#########################################


def test_find_max_in_mapping_one_key() -> None:
    assert objects_are_equal(find_max_in_mapping({"x": 3, "y": 1, "z": 2}), (("x",), 3))


def test_find_max_in_mapping_multiple_keys() -> None:
    assert objects_are_equal(find_max_in_mapping({"a": 10, "b": 20, "c": 20}), (("b", "c"), 20))


def test_find_max_in_mapping_empty() -> None:
    with pytest.raises(ValueError, match=r"Cannot find maximum in an empty mapping"):
        find_max_in_mapping({})
