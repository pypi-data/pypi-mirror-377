r"""Contain DataFrame aggregation functions."""

from __future__ import annotations

__all__ = ["compute_count_aggregated_dataframe"]

import polars as pl

from votingsys.utils.dataframe import check_column_missing


def compute_count_aggregated_dataframe(
    frame: pl.DataFrame, count_col: str = "count"
) -> pl.DataFrame:
    r"""Compute a count aggregated DataFrame.

    Args:
        frame: The DataFrame to compute an aggregated version.
        count_col: The name of the colum that contains the count
            values. This name cannot exist in the DataFrame.

    Returns:
        The aggregated DataFrame. The DataFrame has one additional
            column w.r.t. the input DataFrame.

    Raises:
         ValueError: if the count column exists in the DataFrame.

    Example usage:

    ```pycon

    >>> import polars as pl
    >>> from votingsys.data.aggregation import compute_count_aggregated_dataframe
    >>> out = compute_count_aggregated_dataframe(
    ...     pl.DataFrame(
    ...         {"a": [0, 1, 2, 1, 0, 0], "b": [1, 2, 0, 2, 1, 1], "c": [2, 0, 1, 0, 2, 2]}
    ...     ),
    ... )
    >>> out
    shape: (3, 4)
    ┌─────┬─────┬─────┬───────┐
    │ a   ┆ b   ┆ c   ┆ count │
    │ --- ┆ --- ┆ --- ┆ ---   │
    │ i64 ┆ i64 ┆ i64 ┆ i64   │
    ╞═════╪═════╪═════╪═══════╡
    │ 0   ┆ 1   ┆ 2   ┆ 3     │
    │ 1   ┆ 2   ┆ 0   ┆ 2     │
    │ 2   ┆ 0   ┆ 1   ┆ 1     │
    └─────┴─────┴─────┴───────┘

    ```
    """
    check_column_missing(frame, col=count_col)
    return (
        frame.group_by(frame.columns)
        .agg(pl.len().cast(pl.Int64).alias(count_col))
        .sort(by=count_col, descending=True)
    )
