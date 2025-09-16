from __future__ import annotations

from collections import Counter

import pytest

from votingsys.utils.counter import check_non_empty_count, check_non_negative_count

###########################################
#     Tests for check_non_empty_count     #
###########################################


def test_check_non_empty_count_valid() -> None:
    check_non_empty_count(Counter({"a": 0, "b": 2, "c": 5, "d": 3}))


def test_check_non_empty_count_empty() -> None:
    with pytest.raises(ValueError, match=r"The counter is empty"):
        check_non_empty_count(Counter())


##############################################
#     Tests for check_non_negative_count     #
##############################################


def test_check_non_negative_count_valid() -> None:
    check_non_negative_count(Counter({"a": 0, "b": 2, "c": 5, "d": 3}))


def test_check_non_negative_count_valid_empty() -> None:
    check_non_negative_count(Counter())


def test_check_non_negative_count_invalid() -> None:
    with pytest.raises(ValueError, match=r"The count for 'b' is negative: -2"):
        check_non_negative_count(Counter({"a": 0, "b": -2, "c": 5, "d": 3}))
