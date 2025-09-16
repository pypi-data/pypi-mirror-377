r"""Contain the base class to implement a vote."""

from __future__ import annotations

__all__ = ["BaseVote", "MultipleWinnersFoundError", "WinnerNotFoundError"]

from abc import ABC, abstractmethod
from typing import Any


class BaseVote(ABC):
    r"""Define the base class to implement a vote."""

    @abstractmethod
    def equal(self, other: Any, equal_nan: bool = False) -> bool:
        r"""Indicate if two vote objects are equal or not.

        Args:
            other: The other object to compare.
            equal_nan: Whether to compare NaN's as equal. If ``True``,
                NaN's in both objects will be considered equal.

        Returns:
            ``True`` if the two votes are equal, otherwise ``False``.

        Example usage:

        ```pycon

        >>> from collections import Counter
        >>> from votingsys.vote import SingleMarkVote
        >>> obj1 = SingleMarkVote(Counter({"a": 10, "b": 2, "c": 5, "d": 3}))
        >>> obj2 = SingleMarkVote(Counter({"a": 10, "b": 2, "c": 5, "d": 3}))
        >>> obj3 = SingleMarkVote(Counter({"a": 10, "b": 2}))
        >>> obj1.equal(obj2)
        True
        >>> obj1.equal(obj3)
        False

        ```
        """

    @abstractmethod
    def get_num_candidates(self) -> int:
        r"""Return the number of candidates.

        Returns:
            The number of candidates.

        Example usage:

        ```pycon

        >>> from collections import Counter
        >>> from votingsys.vote import SingleMarkVote
        >>> vote = SingleMarkVote(Counter({"a": 10, "b": 2, "c": 5, "d": 3}))
        >>> vote.get_num_candidates()
        4

        ```
        """

    @abstractmethod
    def get_num_voters(self) -> int:
        r"""Return the number of voters.

        Returns:
            The number of voters.

        Example usage:

        ```pycon

        >>> from collections import Counter
        >>> from votingsys.vote import SingleMarkVote
        >>> vote = SingleMarkVote(Counter({"a": 10, "b": 2, "c": 5, "d": 3}))
        >>> vote.get_num_voters()
        20

        ```
        """


class MultipleWinnersFoundError(Exception):
    r"""Raised when multiple winners are found instead of one."""


class WinnerNotFoundError(Exception):
    r"""Raised when no winner can be found."""
