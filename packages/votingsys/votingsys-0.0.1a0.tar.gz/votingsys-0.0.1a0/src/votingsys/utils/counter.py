r"""Contain counter utility functions."""

from __future__ import annotations

__all__ = ["check_non_empty_count", "check_non_negative_count"]

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections import Counter


def check_non_empty_count(counter: Counter) -> None:
    r"""Check if the counter is not empty.

    Args:
        counter: The counter to check.

    Raises:
        ValueError: if the counter is empty.

    Example usage:

    ```pycon

    >>> from collections import Counter
    >>> from votingsys.utils.counter import check_non_empty_count
    >>> check_non_empty_count(Counter({"a": 10, "b": 2, "c": 5, "d": 3}))

    ```
    """
    if counter.total() == 0:
        msg = "The counter is empty"
        raise ValueError(msg)


def check_non_negative_count(counter: Counter) -> None:
    r"""Check if all the count values are non-negative (>=0).

    Args:
        counter: The counter to check.

    Raises:
        ValueError: if at least one count is negative (<0).

    Example usage:

    ```pycon

    >>> from collections import Counter
    >>> from votingsys.utils.counter import check_non_negative_count
    >>> check_non_negative_count(Counter({"a": 10, "b": 2, "c": 5, "d": 3}))

    ```
    """
    for key, value in counter.items():
        if value < 0:
            msg = f"The count for '{key}' is negative: {value}"
            raise ValueError(msg)
