r"""Contain the implementation of the single-mark vote."""

from __future__ import annotations

__all__ = ["SingleMarkVote"]

from collections import Counter
from typing import TYPE_CHECKING, Any

from coola import objects_are_equal
from coola.utils.format import repr_indent, repr_mapping

from votingsys.utils.counter import check_non_empty_count, check_non_negative_count
from votingsys.utils.dataframe import check_column_exist
from votingsys.utils.mapping import find_max_in_mapping
from votingsys.vote.base import (
    BaseVote,
    MultipleWinnersFoundError,
    WinnerNotFoundError,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

    import polars as pl


class SingleMarkVote(BaseVote):
    r"""Define a single-mark vote.

    This vote assumes that the voter must mark one and only one candidate.

    Args:
        counter: The counter with the number of votes for each candidate.

    Raises:
        ValueError: if at least one count is negative (<0).
        ValueError: if the counter is empty.

    Example usage:

    ```pycon

    >>> from collections import Counter
    >>> from votingsys.vote import SingleMarkVote
    >>> vote = SingleMarkVote(Counter({"a": 10, "b": 2, "c": 5, "d": 3}))
    >>> vote
    SingleMarkVote(
      (counter): Counter({'a': 10, 'c': 5, 'd': 3, 'b': 2})
    )

    ```
    """

    def __init__(self, counter: Counter) -> None:
        check_non_negative_count(counter)
        check_non_empty_count(counter)
        self._counter = counter

    def __repr__(self) -> str:
        args = repr_indent(repr_mapping({"counter": self._counter}))
        return f"{self.__class__.__qualname__}(\n  {args}\n)"

    def equal(self, other: Any, equal_nan: bool = False) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return objects_are_equal(self._counter, other._counter, equal_nan=equal_nan)

    def get_num_candidates(self) -> int:
        return len(self._counter)

    def get_num_voters(self) -> int:
        return self._counter.total()

    def get_candidates(self) -> tuple[str, ...]:
        r"""Get the candidate names.

        Returns:
            The candidate names sorted by alphabetical order.

        Example usage:

        ```pycon

        >>> from collections import Counter
        >>> from votingsys.vote import SingleMarkVote
        >>> vote = SingleMarkVote(Counter({"a": 10, "b": 20, "c": 5, "d": 3}))
        >>> vote.get_candidates()
        ('a', 'b', 'c', 'd')

        ```
        """
        return tuple(sorted(self._counter.keys()))

    def absolute_majority_winner(self) -> str:
        r"""Compute the winner based on the absolute majority rule.

        The candidate receiving more than 50% of the vote is the winner.

        Returns:
            The winner based on the absolute majority rule.

        Raises:
            WinnerNotFoundError: if no candidate has the majority of votes.

        Example usage:

        ```pycon

        >>> from collections import Counter
        >>> from votingsys.vote import SingleMarkVote
        >>> vote = SingleMarkVote(Counter({"a": 10, "b": 20, "c": 5, "d": 3}))
        >>> vote.absolute_majority_winner()
        'b'

        ```
        """
        total_votes = self.get_num_voters()
        candidate, num_votes = self._counter.most_common(1)[0]
        if num_votes / total_votes > 0.5:
            return candidate
        msg = "No winner found using absolute majority rule"
        raise WinnerNotFoundError(msg)

    def super_majority_winner(self, threshold: float) -> str:
        r"""Compute the winner based on the super majority rule.

        The candidate receiving more than X% of the vote is the winner,
        where ``X > 0.5``.

        Args:
            threshold: The minimal threshold to find the super majority
                winner.

        Returns:
            The winner based on the super majority rule.

        Raises:
            WinnerNotFoundError: if no candidate has the super majority of votes.
            ValueError: if the threshold is not valid.

        Example usage:

        ```pycon

        >>> from collections import Counter
        >>> from votingsys.vote import SingleMarkVote
        >>> vote = SingleMarkVote(Counter({"a": 10, "b": 30, "c": 5, "d": 3}))
        >>> vote.super_majority_winner(0.6)
        'b'

        ```
        """
        if threshold <= 0.5:
            msg = f"threshold must be >0.5 (received {threshold})"
            raise ValueError(msg)
        total_votes = self.get_num_voters()
        candidate, num_votes = self._counter.most_common(1)[0]
        if num_votes / total_votes > threshold:
            return candidate
        msg = f"No winner found using super majority rule with threshold={threshold}"
        raise WinnerNotFoundError(msg)

    def plurality_counts(self) -> dict[str, int]:
        r"""Compute the number of votes for each candidate.

        Returns:
            A dictionary with the number of votes for each candidate.
                The key is the candidate and the value is the number
                of votes.

        Example usage:

        ```pycon

        >>> from collections import Counter
        >>> from votingsys.vote import SingleMarkVote
        >>> vote = SingleMarkVote(Counter({"a": 10, "b": 2, "c": 5, "d": 3}))
        >>> vote.plurality_counts()
        {'a': 10, 'b': 2, 'c': 5, 'd': 3}

        ```
        """
        return dict(self._counter)

    def plurality_winner(self) -> str:
        r"""Compute the winner based on the plurality rule.

        This rule is also named First-Past-The-Post (FPTP).
        The leading candidate, whether or not they have a majority of votes, is the winner.

        Returns:
            The winner based on the plurality rule.

        Raises:
            MultipleWinnersFoundError: if the leading candidates are tied.

        Example usage:

        ```pycon

        >>> from collections import Counter
        >>> from votingsys.vote import SingleMarkVote
        >>> vote = SingleMarkVote(Counter({"a": 10, "b": 2, "c": 5, "d": 3}))
        >>> vote.plurality_winner()
        'a'

        ```
        """
        winners = self.plurality_winners()
        if len(winners) > 1:
            msg = f"Multiple winners found using plurality rule: {winners}"
            raise MultipleWinnersFoundError(msg)
        return winners[0]

    def plurality_winners(self) -> tuple[str, ...]:
        r"""Compute the winner(s) based on the plurality rule.

        This rule is also named First-Past-The-Post (FPTP).
        The leading candidate, whether or not they have a majority of votes, is the winner.

        Returns:
            The winners based on the plurality rule. Multiple winners
                can be returned if the leading candidates are tied.
                The candiates are sorted by alphabetical order.

        Example usage:

        ```pycon

        >>> from collections import Counter
        >>> from votingsys.vote import SingleMarkVote
        >>> vote = SingleMarkVote(Counter({"a": 10, "b": 2, "c": 5, "d": 3}))
        >>> vote.plurality_winners()
        ('a',)
        >>> vote = SingleMarkVote(Counter({"a": 10, "b": 2, "c": 5, "d": 10}))
        >>> vote.plurality_winners()
        ('a', 'd')

        ```
        """
        return tuple(sorted(find_max_in_mapping(self._counter)[0]))

    @classmethod
    def from_sequence(cls, votes: Sequence[str]) -> SingleMarkVote:
        r"""Instantiate a ``SingleMarkVote`` object from the sequence of
        votes.

        Args:
            votes: The sequence of votes.

        Returns:
            The instantiated ``SingleMarkVote``.

        Example usage:

        ```pycon

        >>> from votingsys.vote import SingleMarkVote
        >>> vote = SingleMarkVote.from_sequence(["a", "b", "a", "c", "a", "a", "b"])
        >>> vote
        SingleMarkVote(
          (counter): Counter({'a': 4, 'b': 2, 'c': 1})
        )

        ```
        """
        return cls(Counter(votes))

    @classmethod
    def from_series(cls, choices: pl.Series) -> SingleMarkVote:
        r"""Instantiate a ``SingleMarkVote`` object from a
        ``polars.Series`` containing the choices.

        Args:
            choices: The ``polars.Series`` containing the choices.

        Returns:
            The instantiated ``SingleMarkVote``.

        Example usage:

        ```pycon

        >>> import polars as pl
        >>> from votingsys.vote import SingleMarkVote
        >>> vote = SingleMarkVote.from_series(pl.Series(["a", "b", "a", "c", "a", "a", "b"]))
        >>> vote
        SingleMarkVote(
          (counter): Counter({'a': 4, 'b': 2, 'c': 1})
        )

        ```
        """
        return cls.from_sequence(choices.to_list())

    @classmethod
    def from_dataframe(
        cls, frame: pl.DataFrame, choice_col: str, count_col: str | None = None
    ) -> SingleMarkVote:
        r"""Instantiate a ``SingleMarkVote`` object from a
        ``polars.DataFrame`` containing the choices.

        Args:
            frame: The input DataFrame containing the choices.
            choice_col: The column containing the choices.
            count_col: The column containing the count for each choice.
                If ``None``, it assumes the count for each choice is 1.

        Returns:
            The instantiated ``SingleMarkVote``.

        Example usage:

        ```pycon

        >>> import polars as pl
        >>> from votingsys.vote import SingleMarkVote
        >>> # Example without count column
        >>> vote = SingleMarkVote.from_dataframe(
        ...     pl.DataFrame({"first_choice": ["a", "b", "a", "c", "a", "a", "b"]}),
        ...     choice_col="first_choice",
        ... )
        >>> vote
        SingleMarkVote(
          (counter): Counter({'a': 4, 'b': 2, 'c': 1})
        )
        >>> # Example with count column
        >>> vote = SingleMarkVote.from_dataframe(
        ...     pl.DataFrame(
        ...         {
        ...             "first_choice": ["a", "b", "a", "c", "a", "a", "b"],
        ...             "count": [3, 3, 5, 2, 2, 6, 1],
        ...         }
        ...     ),
        ...     choice_col="first_choice",
        ...     count_col="count",
        ... )
        >>> vote
        SingleMarkVote(
          (counter): Counter({'a': 16, 'b': 4, 'c': 2})
        )

        ```
        """
        check_column_exist(frame, choice_col)
        choices = frame[choice_col].to_list()
        counts = [1] * len(choices)
        if count_col is not None:
            check_column_exist(frame, count_col)
            counts = frame[count_col].to_list()
        counter = Counter()
        for choice, count in zip(choices, counts):
            counter[choice] += count
        return cls(counter)
