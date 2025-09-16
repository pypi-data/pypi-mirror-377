r"""Contain mapping utility functions."""

from __future__ import annotations

__all__ = ["find_max_in_mapping"]

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping


def find_max_in_mapping(mapping: Mapping[str, float]) -> tuple[tuple[str, ...], float]:
    """Find the maximum value in a mapping and returns the corresponding
    key(s) and the value.

    If multiple keys have the same maximum value, all such keys are
    returned in a list.

    Args:
        mapping: A mapping from keys to numeric values.

    Returns:
        A tuple containing the tuple of keys with the maximum value
            and the maximum value itself.

    Raises:
        ValueError: if the mapping is empty.

    Example usage:

    ```pycon

    >>> import polars as pl
    >>> from votingsys.utils.mapping import find_max_in_mapping
    >>> out = find_max_in_mapping({"x": 3, "y": 1})
    >>> out
    (('x',), 3)
    >>> out = find_max_in_mapping({"a": 10, "b": 20, "c": 20})
    >>> out
    (('b', 'c'), 20)

    ```
    """
    if not mapping:
        msg = "Cannot find maximum in an empty mapping"
        raise ValueError(msg)

    max_value = max(mapping.values())
    keys_with_max = tuple(k for k, v in mapping.items() if v == max_value)
    return keys_with_max, max_value
