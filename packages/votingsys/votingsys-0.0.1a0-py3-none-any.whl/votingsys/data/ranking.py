r"""Contain functions to manage a DataFrame with rankings."""

from __future__ import annotations

__all__ = ["is_valid_linear_ranking"]

import polars as pl


def is_valid_linear_ranking(frame_rank: pl.DataFrame) -> bool:
    r"""Indicate if the input DataFrame contains a linear ranking for
    each row.

    A linear ranking is ranking that goes from ``0`` to ``n-1``,
    where ``n`` is the number of columns.

    Args:
        frame_rank: The DataFrame with the ranking.
            Each column represents a candidate.

    Returns:
        ``True`` if the DataFrame contains a linear ranking for
            each row, otherwise ``False``.

    Example usage:

    ```pycon

    >>> import polars as pl
    >>> from votingsys.data.ranking import is_valid_linear_ranking
    >>> is_valid_linear_ranking(
    ...     pl.DataFrame({"a": [0, 1, 2, 1, 0], "b": [1, 2, 0, 2, 1], "c": [2, 0, 1, 0, 2]})
    ... )
    True

    ```
    """
    if not frame_rank.shape[0]:
        return True

    values = tuple(range(frame_rank.shape[1]))
    return frame_rank.select(pl.concat_list(pl.all()).list.sort().eq(values).all()).item()
