from __future__ import annotations

import polars as pl
import pytest
from coola import objects_are_equal

from votingsys.utils.dataframe import (
    check_column_exist,
    check_column_missing,
    remove_zero_weight_rows,
    sum_weights_by_group,
    value_count,
    weighted_value_count,
)

########################################
#     Tests for check_column_exist     #
########################################


def test_check_column_exist() -> None:
    check_column_exist(
        pl.DataFrame({"a": [1, 2, 3], "b": ["a", "b", "c"], "c": [1.1, 2.2, 3.3]}), col="a"
    )


def test_check_column_exist_missing() -> None:
    with pytest.raises(ValueError, match=r"column 'd' is missing in the DataFrame:"):
        check_column_exist(
            pl.DataFrame({"a": [1, 2, 3], "b": ["a", "b", "c"], "c": [1.1, 2.2, 3.3]}), col="d"
        )


##########################################
#     Tests for check_column_missing     #
##########################################


def test_check_column_missing() -> None:
    check_column_missing(
        pl.DataFrame({"a": [1, 2, 3], "b": ["a", "b", "c"], "c": [1.1, 2.2, 3.3]}), col="col"
    )


def test_check_column_missing_empty() -> None:
    check_column_missing(pl.DataFrame({}), col="col")


def test_check_column_missing_exist() -> None:
    with pytest.raises(ValueError, match=r"column 'a' exists in the DataFrame:"):
        check_column_missing(
            pl.DataFrame({"a": [1, 2, 3], "b": ["a", "b", "c"], "c": [1.1, 2.2, 3.3]}), col="a"
        )


############################################
#     Tests for value_count     #
############################################


@pytest.mark.parametrize(
    ("value", "counts"),
    [
        (0, {"a": 2, "b": 1, "c": 2}),
        (1, {"a": 2, "b": 2, "c": 1}),
        (2, {"a": 1, "b": 2, "c": 2}),
        (3, {"a": 0, "b": 0, "c": 0}),
    ],
)
def test_value_count(value: int, counts: dict) -> None:
    assert objects_are_equal(
        value_count(
            pl.DataFrame({"a": [0, 1, 2, 1, 0], "b": [1, 2, 0, 2, 1], "c": [2, 0, 1, 0, 2]}),
            value=value,
        ),
        counts,
    )


@pytest.mark.parametrize(
    ("value", "counts"),
    [
        (0, {"a": 2, "b": 1, "c": 2}),
        (1, {"a": 1, "b": 2, "c": 1}),
        (2, {"a": 1, "b": 2, "c": 1}),
        (3, {"a": 0, "b": 0, "c": 0}),
    ],
)
def test_value_count_with_nulls(value: int, counts: dict) -> None:
    assert objects_are_equal(
        value_count(
            pl.DataFrame({"a": [0, 1, 2, None, 0], "b": [1, 2, 0, 2, 1], "c": [None, 0, 1, 0, 2]}),
            value=value,
        ),
        counts,
    )


def test_value_count_empty() -> None:
    assert objects_are_equal(value_count(pl.DataFrame(), value=1), {})


def test_value_count_value_none() -> None:
    with pytest.raises(ValueError, match=r"value cannot be None"):
        value_count(pl.DataFrame(), value=None)


##########################################
#     Tests for weighted_value_count     #
##########################################


@pytest.mark.parametrize(
    ("value", "counts"),
    [
        (0, {"a": 3, "b": 2, "c": 6}),
        (1, {"a": 5, "b": 4, "c": 2}),
        (2, {"a": 3, "b": 5, "c": 3}),
        (3, {"a": 0, "b": 0, "c": 0}),
    ],
)
def test_weighted_value_count(value: int, counts: dict) -> None:
    assert objects_are_equal(
        weighted_value_count(
            pl.DataFrame(
                {"a": [0, 1, 2, 2], "b": [1, 2, 0, 1], "c": [2, 0, 1, 0], "count": [3, 5, 2, 1]}
            ),
            value=value,
            weight_col="count",
        ),
        counts,
    )


@pytest.mark.parametrize(
    ("value", "counts"),
    [
        (0, {"a": 3, "b": 2, "c": 1}),
        (1, {"a": 5, "b": 4, "c": 2}),
        (2, {"a": 1, "b": 5, "c": 3}),
        (3, {"a": 0, "b": 0, "c": 0}),
    ],
)
def test_weighted_value_count_with_nulls(value: int, counts: dict) -> None:
    assert objects_are_equal(
        weighted_value_count(
            pl.DataFrame(
                {
                    "a": [0, 1, None, 2],
                    "b": [1, 2, 0, 1],
                    "c": [2, None, 1, 0],
                    "count": [3, 5, 2, 1],
                }
            ),
            value=value,
            weight_col="count",
        ),
        counts,
    )


@pytest.mark.parametrize(
    ("value", "counts"),
    [
        (0, {"a": 2.5, "b": 1.0, "c": 1.7}),
        (1, {"a": 0.5, "b": 3.7, "c": 1.0}),
        (2, {"a": 2.2, "b": 0.5, "c": 2.5}),
        (3, {"a": 0.0, "b": 0.0, "c": 0.0}),
    ],
)
def test_weighted_value_count_float_weight(value: int, counts: dict) -> None:
    assert objects_are_equal(
        weighted_value_count(
            pl.DataFrame(
                {
                    "a": [0, 1, 2, 2],
                    "b": [1, 2, 0, 1],
                    "c": [2, 0, 1, 0],
                    "count": [2.5, 0.5, 1.0, 1.2],
                }
            ),
            value=value,
            weight_col="count",
        ),
        counts,
    )


def test_weighted_value_count_empty() -> None:
    with pytest.raises(ValueError, match=r"column 'count' is missing in the DataFrame"):
        weighted_value_count(pl.DataFrame(), value=1, weight_col="count")


#############################################
#     Tests for remove_zero_weight_rows     #
#############################################


def test_remove_zero_weight_rows() -> None:
    assert objects_are_equal(
        remove_zero_weight_rows(
            pl.DataFrame(
                {
                    "a": [0, 1, 2, 2, 0],
                    "b": [1, 2, 0, 1, 2],
                    "c": [2, 0, 1, 0, 1],
                    "weight": [3, 0, 2, 1, 0],
                }
            ),
            weight_col="weight",
        ),
        pl.DataFrame({"a": [0, 2, 2], "b": [1, 0, 1], "c": [2, 1, 0], "weight": [3, 2, 1]}),
    )


def test_remove_zero_weight_rows_empty() -> None:
    assert objects_are_equal(
        remove_zero_weight_rows(
            pl.DataFrame({"a": [], "b": [], "c": [], "weight": []}),
            weight_col="weight",
        ),
        pl.DataFrame({"a": [], "b": [], "c": [], "weight": []}),
    )


def test_remove_zero_weight_rows_no_zeros() -> None:
    assert objects_are_equal(
        remove_zero_weight_rows(
            pl.DataFrame(
                {
                    "a": [0, 1, 2, 2, 0],
                    "b": [1, 2, 0, 1, 2],
                    "c": [2, 0, 1, 0, 1],
                    "weight": [3, 5, 2, 1, 7],
                }
            ),
            weight_col="weight",
        ),
        pl.DataFrame(
            {
                "a": [0, 1, 2, 2, 0],
                "b": [1, 2, 0, 1, 2],
                "c": [2, 0, 1, 0, 1],
                "weight": [3, 5, 2, 1, 7],
            }
        ),
    )


def test_remove_zero_weight_rows_missing_column() -> None:
    frame = pl.DataFrame(
        {
            "a": [0, 1, 2, 2, 0],
            "b": [1, 2, 0, 1, 2],
            "c": [2, 0, 1, 0, 1],
            "weight": [3, 0, 2, 1, 0],
        }
    )
    with pytest.raises(ValueError, match=r"column 'count' is missing in the DataFrame"):
        remove_zero_weight_rows(frame, weight_col="count")


##########################################
#     Tests for sum_weights_by_group     #
##########################################


def test_sum_weights_by_group() -> None:
    assert objects_are_equal(
        sum_weights_by_group(
            pl.DataFrame(
                {
                    "a": [0, 1, 2, 0, 1, 2],
                    "b": [1, 2, 0, 1, 2, 0],
                    "c": [2, 0, 1, 2, 0, 1],
                    "weight": [3, 5, 2, 1, 2, -2],
                }
            ),
            weight_col="weight",
        ).sort("weight", descending=True),
        pl.DataFrame(
            {
                "a": [1, 0, 2],
                "b": [2, 1, 0],
                "c": [0, 2, 1],
                "weight": [7, 4, 0],
            }
        ),
    )


def test_sum_weights_by_group_empty() -> None:
    assert objects_are_equal(
        sum_weights_by_group(
            pl.DataFrame({"a": [], "b": [], "c": [], "weight": []}),
            weight_col="weight",
        ),
        pl.DataFrame({"a": [], "b": [], "c": [], "weight": []}),
    )


def test_sum_weights_by_group_unique() -> None:
    assert objects_are_equal(
        sum_weights_by_group(
            pl.DataFrame(
                {
                    "a": [1, 0, 2],
                    "b": [2, 1, 0],
                    "c": [0, 2, 1],
                    "weight": [7, 4, 0],
                }
            ),
            weight_col="weight",
        ).sort("weight", descending=True),
        pl.DataFrame(
            {
                "a": [1, 0, 2],
                "b": [2, 1, 0],
                "c": [0, 2, 1],
                "weight": [7, 4, 0],
            }
        ),
    )


def test_sum_weights_by_group_one() -> None:
    assert objects_are_equal(
        sum_weights_by_group(
            pl.DataFrame({"a": ["x", "x", "x", "x"], "b": [1, 1, 1, 1], "weight": [7, 4, 0, 2]}),
            weight_col="weight",
        ).sort("weight", descending=True),
        pl.DataFrame({"a": ["x"], "b": [1], "weight": [13]}),
    )


def test_weighted_value_count_missing_column() -> None:
    frame = pl.DataFrame(
        {
            "a": [0, 1, 2, 0, 1, 2],
            "b": [1, 2, 0, 1, 2, 0],
            "c": [2, 0, 1, 2, 0, 1],
            "weight": [3, 5, 2, 1, 2, -2],
        }
    )
    with pytest.raises(ValueError, match=r"column 'count' is missing in the DataFrame"):
        sum_weights_by_group(frame, weight_col="count")
