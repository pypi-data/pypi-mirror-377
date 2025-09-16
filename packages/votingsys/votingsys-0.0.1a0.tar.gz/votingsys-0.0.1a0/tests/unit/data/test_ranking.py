from __future__ import annotations

import polars as pl

from votingsys.data.ranking import is_valid_linear_ranking

#############################################
#     Tests for is_valid_linear_ranking     #
#############################################


def test_is_valid_linear_ranking_true() -> None:
    assert is_valid_linear_ranking(
        pl.DataFrame({"a": [0, 1, 2, 1, 0], "b": [1, 2, 0, 2, 1], "c": [2, 0, 1, 0, 2]})
    )


def test_is_valid_linear_ranking_false_repeated_value() -> None:
    assert not is_valid_linear_ranking(
        pl.DataFrame({"a": [0, 1, 2, 1, 0], "b": [1, 2, 0, 2, 1], "c": [2, 0, 1, 0, 0]})
    )


def test_is_valid_linear_ranking_false_incorrect_value() -> None:
    assert not is_valid_linear_ranking(
        pl.DataFrame({"a": [0, 1, 2, 1, 0], "b": [1, 2, 0, 2, 1], "c": [2, 0, 1, 0, 111]})
    )


def test_is_valid_linear_ranking_empty() -> None:
    assert is_valid_linear_ranking(pl.DataFrame({}))
