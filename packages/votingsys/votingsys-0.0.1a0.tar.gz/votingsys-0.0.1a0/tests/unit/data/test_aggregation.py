from __future__ import annotations

import polars as pl
import pytest

from votingsys.data.aggregation import compute_count_aggregated_dataframe

########################################################
#     Tests for compute_count_aggregated_dataframe     #
########################################################


def test_compute_count_aggregated_dataframe() -> None:
    pl.testing.assert_frame_equal(
        compute_count_aggregated_dataframe(
            pl.DataFrame(
                {
                    "a": [1, 1, 1, 1, 1, 0, 0, 2, 2, 2, 2, 2, 2, 2],
                    "b": [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                    "c": [2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0],
                },
                schema={"a": pl.Int64, "b": pl.Int64, "c": pl.Int64},
            )
        ),
        pl.DataFrame(
            {"a": [2, 1, 0], "b": [1, 0, 1], "c": [0, 2, 2], "count": [7, 5, 2]},
            schema={"a": pl.Int64, "b": pl.Int64, "c": pl.Int64, "count": pl.Int64},
        ),
    )


def test_compute_count_aggregated_dataframe_empty() -> None:
    pl.testing.assert_frame_equal(
        compute_count_aggregated_dataframe(
            pl.DataFrame(
                {"a": [], "b": [], "c": []}, schema={"a": pl.Int64, "b": pl.Int64, "c": pl.Int64}
            )
        ),
        pl.DataFrame(
            {"a": [], "b": [], "c": [], "count": []},
            schema={"a": pl.Int64, "b": pl.Int64, "c": pl.Int64, "count": pl.Int64},
        ),
    )


def test_compute_count_aggregated_dataframe_count_col() -> None:
    pl.testing.assert_frame_equal(
        compute_count_aggregated_dataframe(
            pl.DataFrame(
                {
                    "a": [1, 1, 1, 1, 1, 0, 0, 2, 2, 2, 2, 2, 2, 2],
                    "b": [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                    "c": [2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0],
                },
                schema={"a": pl.Int64, "b": pl.Int64, "c": pl.Int64},
            ),
            count_col="#count",
        ),
        pl.DataFrame(
            {"a": [2, 1, 0], "b": [1, 0, 1], "c": [0, 2, 2], "#count": [7, 5, 2]},
            schema={"a": pl.Int64, "b": pl.Int64, "c": pl.Int64, "#count": pl.Int64},
        ),
    )


def test_compute_count_aggregated_dataframe_count_col_exist() -> None:
    frame = pl.DataFrame(
        {
            "a": [1, 1, 1, 1, 1, 0, 0, 2, 2, 2, 2, 2, 2, 2],
            "b": [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            "c": [2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0],
        },
        schema={"a": pl.Int64, "b": pl.Int64, "c": pl.Int64},
    )
    with pytest.raises(ValueError, match=r"column 'c' exists in the DataFrame:"):
        compute_count_aggregated_dataframe(frame, count_col="c")
