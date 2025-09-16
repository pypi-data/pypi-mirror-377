r"""Contain DataFrame utility functions."""

from __future__ import annotations

__all__ = [
    "check_column_exist",
    "check_column_missing",
    "remove_zero_weight_rows",
    "sum_weights_by_group",
    "value_count",
    "weighted_value_count",
]

from typing import Any

import polars as pl


def check_column_exist(frame: pl.DataFrame, col: str) -> None:
    r"""Check if a column exists in a DataFrame.

    Args:
        frame: The DataFrame to check.
        col: The column that should exist in the DataFrame.

    Raises:
        ValueError: if the column is missing in the DataFrame.

    Example usage:

    ```pycon

    >>> import polars as pl
    >>> from votingsys.utils.dataframe import check_column_exist
    >>> check_column_exist(
    ...     pl.DataFrame({"a": [0, 1, 2, 1, 0], "b": [1, 2, 0, 2, 1], "c": [2, 0, 1, 0, 2]}),
    ...     col="a",
    ... )

    ```
    """
    if col not in frame:
        msg = f"column '{col}' is missing in the DataFrame: {sorted(frame.columns)}"
        raise ValueError(msg)


def check_column_missing(frame: pl.DataFrame, col: str) -> None:
    r"""Check if a column is missing in a DataFrame.

    Args:
        frame: The DataFrame to check.
        col: The column that should be missing in the DataFrame.

    Raises:
        ValueError: if the column exists in the DataFrame.

    Example usage:

    ```pycon

    >>> import polars as pl
    >>> from votingsys.utils.dataframe import check_column_missing
    >>> check_column_missing(
    ...     pl.DataFrame({"a": [0, 1, 2, 1, 0], "b": [1, 2, 0, 2, 1], "c": [2, 0, 1, 0, 2]}),
    ...     col="col",
    ... )

    ```
    """
    if col in frame:
        msg = f"column '{col}' exists in the DataFrame: {sorted(frame.columns)}"
        raise ValueError(msg)


def value_count(frame: pl.DataFrame, value: Any) -> dict[str, int]:
    r"""Count the occurrences of a given value in each column of a
    DataFrame.

    This function computes how many times a specified value appears in
    each column. Null values are ignored during the counting process.

    Args:
        frame: The input DataFrame.
        value: The value to count in each column.

    Returns:
        A dictionary mapping each column name to the number of times
            the specified value appears.

    Raises:
        ValueError: If the specified value is ``None``.

    Example usage:

    ```pycon

    >>> import polars as pl
    >>> from votingsys.utils.dataframe import value_count
    >>> counts = value_count(
    ...     pl.DataFrame({"a": [0, 1, 2, 1, 0], "b": [1, 2, 0, 2, 1], "c": [2, 0, 1, 0, 2]}),
    ...     value=1,
    ... )
    >>> counts
    {'a': 2, 'b': 2, 'c': 1}

    ```
    """
    if value is None:
        msg = "value cannot be None"
        raise ValueError(msg)
    counts = frame.select(
        [
            ((pl.col(col) == value) & pl.col(col).is_not_null()).sum().alias(col)
            for col in frame.columns
        ]
    ).to_dict(as_series=False)
    return {key: value[0] for key, value in counts.items()}


def weighted_value_count(
    frame: pl.DataFrame, value: int, weight_col: str
) -> dict[str, int | float]:
    r"""Count the weighted occurrences of a given value in each column of
    a DataFrame.

    This function computes how many times a specified value appears in
    each column, weighted by the values in a separate count column.
    Null values are ignored during the counting process.

    Args:
        frame: The input DataFrame.
        value: The value to count in each column.
        weight_col: The name of the column that holds the weight for
            each row.

    Returns:
        A dictionary mapping each column name (excluding the count
            column) to the weighted number of times the specified
            value appears.

    Raises:
        ValueError: if the weight column is missing in the DataFrame.

    Example usage:

    ```pycon

    >>> import polars as pl
    >>> from votingsys.utils.dataframe import weighted_value_count
    >>> counts = weighted_value_count(
    ...     pl.DataFrame({"a": [0, 1, 2], "b": [1, 2, 0], "c": [2, 0, 1], "count": [3, 5, 2]}),
    ...     value=1,
    ...     weight_col="count",
    ... )
    >>> counts
    {'a': 5, 'b': 3, 'c': 2}

    ```
    """
    check_column_exist(frame, weight_col)
    counts = frame.select(
        [
            (
                ((pl.col(col) == value) & pl.col(col).is_not_null()).cast(pl.Int32)
                * pl.col(weight_col)
            )
            .sum()
            .alias(col)
            for col in frame.columns
            if col != weight_col
        ]
    ).to_dict(as_series=False)
    return {key: value[0] for key, value in counts.items()}


def remove_zero_weight_rows(frame: pl.DataFrame, weight_col: str) -> pl.DataFrame:
    """Remove all rows from a DataFrame where the weight value is zero.

    Args:
        frame: The input DataFrame from which rows should be filtered.
        weight_col:  The name of the column that contains the weight
            values.

    Returns:
        A new DataFrame with all rows removed where the weight is zero.

    Raises:
        ValueError: if ``weight_col`` does not exist in the DataFrame.

    Example usage:

    ```pycon

    >>> import polars as pl
    >>> from votingsys.utils.dataframe import remove_zero_weight_rows
    >>> out = remove_zero_weight_rows(
    ...     pl.DataFrame(
    ...         {
    ...             "a": [0, 1, 2, 0, 1, 2],
    ...             "b": [1, 2, 0, 1, 2, 0],
    ...             "c": [2, 0, 1, 2, 0, 1],
    ...             "weight": [3, 0, 2, 1, 2, 0],
    ...         }
    ...     ),
    ...     weight_col="weight",
    ... )
    >>> out
    shape: (4, 4)
    ┌─────┬─────┬─────┬────────┐
    │ a   ┆ b   ┆ c   ┆ weight │
    │ --- ┆ --- ┆ --- ┆ ---    │
    │ i64 ┆ i64 ┆ i64 ┆ i64    │
    ╞═════╪═════╪═════╪════════╡
    │ 0   ┆ 1   ┆ 2   ┆ 3      │
    │ 2   ┆ 0   ┆ 1   ┆ 2      │
    │ 0   ┆ 1   ┆ 2   ┆ 1      │
    │ 1   ┆ 2   ┆ 0   ┆ 2      │
    └─────┴─────┴─────┴────────┘

    ```
    """
    check_column_exist(frame, weight_col)
    return frame.filter(pl.col(weight_col) != 0)


def sum_weights_by_group(frame: pl.DataFrame, weight_col: str) -> pl.DataFrame:
    """Aggregate a DataFrame by summing the weight values for rows with
    identical values in all columns except the weight column.

    Args:
        frame: The input DataFrame to aggregate.
        weight_col: The name of the column that contains the weight
            values to be summed.

    Returns:
            A new DataFrame with rows grouped by all non-weight columns,
            and the weight column summed within each group.

    Raises:
        ValueError: if ``weight_col`` does not exist in the DataFrame.

    Example usage:

    ```pycon

    >>> import polars as pl
    >>> from votingsys.utils.dataframe import sum_weights_by_group
    >>> out = sum_weights_by_group(
    ...     pl.DataFrame(
    ...         {
    ...             "a": [0, 1, 2, 0, 1, 2],
    ...             "b": [1, 2, 0, 1, 2, 0],
    ...             "c": [2, 0, 1, 2, 0, 1],
    ...             "weight": [3, 5, 2, 1, 2, -2],
    ...         }
    ...     ),
    ...     weight_col="weight",
    ... )
    >>> out.sort("weight", descending=True)
    shape: (3, 4)
    ┌─────┬─────┬─────┬────────┐
    │ a   ┆ b   ┆ c   ┆ weight │
    │ --- ┆ --- ┆ --- ┆ ---    │
    │ i64 ┆ i64 ┆ i64 ┆ i64    │
    ╞═════╪═════╪═════╪════════╡
    │ 1   ┆ 2   ┆ 0   ┆ 7      │
    │ 0   ┆ 1   ┆ 2   ┆ 4      │
    │ 2   ┆ 0   ┆ 1   ┆ 0      │
    └─────┴─────┴─────┴────────┘

    ```
    """
    check_column_exist(frame, weight_col)
    group_cols = [col for col in frame.columns if col != weight_col]
    return frame.group_by(group_cols).agg(pl.col(weight_col).sum().alias(weight_col))
