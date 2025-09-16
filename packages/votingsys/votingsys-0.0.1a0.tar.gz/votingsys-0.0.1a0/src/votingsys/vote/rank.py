r"""Contain the implementation of the ranked vote."""

from __future__ import annotations

__all__ = ["RankedVote", "compute_borda_count"]

from typing import TYPE_CHECKING, Any

from black.trans import defaultdict
from coola import objects_are_equal

from votingsys.data.aggregation import compute_count_aggregated_dataframe
from votingsys.utils.dataframe import (
    check_column_exist,
    remove_zero_weight_rows,
    sum_weights_by_group,
    weighted_value_count,
)
from votingsys.utils.mapping import find_max_in_mapping
from votingsys.vote.base import (
    BaseVote,
    MultipleWinnersFoundError,
    WinnerNotFoundError,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

    import polars as pl


class RankedVote(BaseVote):
    r"""Define the ranked vote.

    A ranked vote, also known as a preferential vote, is a voting
    system in which voters rank candidates or options in order of
    preference, rather than choosing just one.

    Args:
        ranking: A DataFrame with the ranking for each voter. Each
            column represents a candidate, and each row is a voter
            ranking. The ranking goes from ``0`` to ``n-1``, where
            ``n`` is the number of candidates. One column contains
            the number of voters for this ranking.
        count_col: The column with the count data for each ranking.

    Example usage:

    ```pycon

    >>> import polars as pl
    >>> from votingsys.vote import RankedVote
    >>> vote = RankedVote(
    ...     pl.DataFrame({"a": [0, 1, 2], "b": [1, 2, 0], "c": [2, 0, 1], "count": [3, 5, 2]})
    ... )
    >>> vote
    RankedVote(num_candidates=3, num_voters=10, count_col='count')
    >>> vote.ranking
    shape: (3, 4)
    ┌─────┬─────┬─────┬───────┐
    │ a   ┆ b   ┆ c   ┆ count │
    │ --- ┆ --- ┆ --- ┆ ---   │
    │ i64 ┆ i64 ┆ i64 ┆ i64   │
    ╞═════╪═════╪═════╪═══════╡
    │ 0   ┆ 1   ┆ 2   ┆ 3     │
    │ 1   ┆ 2   ┆ 0   ┆ 5     │
    │ 2   ┆ 0   ┆ 1   ┆ 2     │
    └─────┴─────┴─────┴───────┘

    ```
    """

    def __init__(self, ranking: pl.DataFrame, count_col: str = "count") -> None:
        check_column_exist(ranking, count_col)
        self._ranking = ranking
        self._count_col = count_col

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__qualname__}(num_candidates={self.get_num_candidates():,}, "
            f"num_voters={self.get_num_voters():,}, count_col={self._count_col!r})"
        )

    @property
    def ranking(self) -> pl.DataFrame:
        r"""Return the DataFrame containing the rankings."""
        return self._ranking

    def equal(self, other: Any, equal_nan: bool = False) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return objects_are_equal(self._ranking, other._ranking, equal_nan=equal_nan)

    def get_num_candidates(self) -> int:
        return self._ranking.shape[1] - 1

    def get_num_voters(self) -> int:
        return self._ranking[self._count_col].sum()

    def get_candidates(self) -> tuple[str, ...]:
        r"""Get the candidate names.

        Returns:
            The candidate names sorted by alphabetical order.

        Example usage:

        ```pycon

        >>> import polars as pl
        >>> from votingsys.vote import RankedVote
        >>> vote = RankedVote.from_dataframe_with_count(
        ...     pl.DataFrame({"a": [0, 1, 2], "b": [1, 2, 0], "c": [2, 0, 1], "count": [3, 6, 2]}),
        ... )
        >>> vote.get_candidates()
        ('a', 'b', 'c')

        ```
        """
        return tuple(sorted([col for col in self._ranking.columns if col != self._count_col]))

    def absolute_majority_winner(self) -> str:
        r"""Compute the winner based on the absolute majority rule.

        The candidate receiving more than 50% of the vote is the winner.

        Returns:
            The winner based on the absolute majority rule.

        Raises:
            WinnerNotFoundError: if no candidate has the majority of votes.

        Example usage:

        ```pycon

        >>> import polars as pl
        >>> from votingsys.vote import RankedVote
        >>> vote = RankedVote.from_dataframe_with_count(
        ...     pl.DataFrame({"a": [0, 1, 2], "b": [1, 2, 0], "c": [2, 0, 1], "count": [3, 6, 2]}),
        ... )
        >>> vote.absolute_majority_winner()
        'c'

        ```
        """
        candidates, max_votes = find_max_in_mapping(self.plurality_counts())
        total_votes = self.get_num_voters()
        if max_votes / total_votes > 0.5:
            return candidates[0]
        msg = "No winner found using absolute majority rule"
        raise WinnerNotFoundError(msg)

    def borda_counts(self, points: Sequence | None = None) -> dict[str, float]:
        r"""Compute the Borda count for each candidate.

        The Borda count method is a ranked voting system where voters
        list candidates in order of preference. Points are assigned
        based on position in each ranking. For example, in an election
        with n candidates, a first-place vote earns n points, second
        place gets n-1, and so on, down to 1. The candidate with the
        highest total score across all votes wins. This method
        considers the overall preferences of voters, not just their
        top choices.

        Args:
            points: The points associated for each rank. The first value
                is the point for rank 0, the second value is the point
                for rank 1, etc. The number of points must be equal to
                the number of candidates. If no points is given, the
                default points are ``[n, n-1, n-2, ..., 1]``

        Returns:
            A dictionary with the Borda count for each candidate.
                The key is the candidate and the value is the Borda
                count.

        Example usage:

        ```pycon

        >>> import polars as pl
        >>> from votingsys.vote import RankedVote
        >>> vote = RankedVote.from_dataframe_with_count(
        ...     pl.DataFrame({"a": [0, 1, 2], "b": [1, 2, 0], "c": [2, 0, 1], "count": [3, 5, 2]}),
        ... )
        >>> vote.borda_counts()
        {'a': 21.0, 'b': 17.0, 'c': 22.0}

        ```
        """
        if points is None:
            points = list(range(self.get_num_candidates(), 0, -1))
        return compute_borda_count(self.ranking, points=points, count_col=self._count_col)

    def borda_count_winner(self, points: Sequence | None = None) -> str:
        r"""Compute the winner based on the Borda count rule.

        The Borda count method is a ranked voting system where voters
        list candidates in order of preference. Points are assigned
        based on position in each ranking. For example, in an election
        with n candidates, a first-place vote earns n points, second
        place gets n-1, and so on, down to 1. The candidate with the
        highest total score across all votes wins. This method
        considers the overall preferences of voters, not just their
        top choices.

        Args:
            points: The points associated for each rank. The first value
                is the point for rank 0, the second value is the point
                for rank 1, etc. The number of points must be equal to
                the number of candidates. If no points is given, the
                default points are ``[n, n-1, n-2, ..., 1]``

        Returns:
            The winner based on the Borda count rule.

        Raises:
            MultipleWinnersFoundError: if the leading candidates are tied.

        Example usage:

        ```pycon

        >>> import polars as pl
        >>> from votingsys.vote import RankedVote
        >>> vote = RankedVote.from_dataframe_with_count(
        ...     pl.DataFrame({"a": [0, 1, 2], "b": [1, 2, 0], "c": [2, 0, 1], "count": [3, 5, 2]}),
        ... )
        >>> vote.borda_count_winner()
        'c'

        ```
        """
        winners = self.borda_count_winners(points=points)
        if len(winners) > 1:
            msg = f"Multiple winners found using Borda count rule: {winners}"
            raise MultipleWinnersFoundError(msg)
        return winners[0]

    def borda_count_winners(self, points: Sequence | None = None) -> tuple[str, ...]:
        r"""Compute the winner(s) based on the Borda count rule.

        The Borda count method is a ranked voting system where voters
        list candidates in order of preference. Points are assigned
        based on position in each ranking. For example, in an election
        with n candidates, a first-place vote earns n points, second
        place gets n-1, and so on, down to 1. The candidate with the
        highest total score across all votes wins. This method
        considers the overall preferences of voters, not just their
        top choices.

        Args:
            points: The points associated for each rank. The first value
                is the point for rank 0, the second value is the point
                for rank 1, etc. The number of points must be equal to
                the number of candidates. If no points is given, the
                default points are ``[n, n-1, n-2, ..., 1]``

        Returns:
            The winners based on the Borda count rule. Multiple winners
                can be returned if the leading candidates are tied.
                The candiates are sorted by alphabetical order.

        Example usage:

        ```pycon

        >>> import polars as pl
        >>> from votingsys.vote import RankedVote
        >>> vote = RankedVote.from_dataframe_with_count(
        ...     pl.DataFrame({"a": [0, 1, 2], "b": [1, 2, 0], "c": [2, 0, 1], "count": [3, 5, 2]}),
        ... )
        >>> vote.borda_count_winners()
        ('c',)
        >>> vote = RankedVote.from_dataframe_with_count(
        ...     pl.DataFrame({"a": [0, 1, 2], "b": [1, 0, 2], "c": [2, 0, 1], "count": [1, 1, 1]}),
        ... )
        >>> vote.borda_count_winners(points=[4, 2, 1])
        ('a', 'b', 'c')

        ```
        """
        candidates, _ = find_max_in_mapping(self.borda_counts(points=points))
        return tuple(sorted(candidates))

    def plurality_counts(self) -> dict[str, int]:
        r"""Compute the plurality count for each candidate, i.e. the
        number of voters who rank each candidate in first place.

        Returns:
            A dictionary with the count of votes for each candidate.
                The key is the candidate and the value is the number
                of votes.

        Example usage:

        ```pycon

        >>> import polars as pl
        >>> from votingsys.vote import RankedVote
        >>> vote = RankedVote.from_dataframe_with_count(
        ...     pl.DataFrame({"a": [0, 1, 2], "b": [1, 2, 0], "c": [2, 0, 1], "count": [3, 6, 2]}),
        ... )
        >>> vote.plurality_counts()
        {'a': 3, 'b': 2, 'c': 6}

        ```
        """
        return weighted_value_count(self._ranking, value=0, weight_col=self._count_col)

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

        >>> import polars as pl
        >>> from votingsys.vote import RankedVote
        >>> vote = RankedVote.from_dataframe_with_count(
        ...     pl.DataFrame({"a": [0, 1, 2], "b": [1, 2, 0], "c": [2, 0, 1], "count": [3, 6, 2]}),
        ... )
        >>> vote.plurality_winner()
        'c'

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

        >>> import polars as pl
        >>> from votingsys.vote import RankedVote
        >>> vote = RankedVote.from_dataframe_with_count(
        ...     pl.DataFrame({"a": [0, 1, 2], "b": [1, 2, 0], "c": [2, 0, 1], "count": [3, 6, 2]}),
        ... )
        >>> vote.plurality_winners()
        ('c',)
        >>> vote = RankedVote.from_dataframe_with_count(
        ...     pl.DataFrame(
        ...         {"a": [0, 1, 2, 1], "b": [1, 2, 0, 0], "c": [2, 0, 1, 2], "count": [3, 6, 2, 4]}
        ...     ),
        ... )
        >>> vote.plurality_winners()
        ('b', 'c')

        ```
        """
        candidates, _ = find_max_in_mapping(self.plurality_counts())
        return tuple(sorted(candidates))

    @classmethod
    def from_dataframe(cls, ranking: pl.DataFrame, count_col: str = "count") -> RankedVote:
        r"""Instantiate a ``RankedVote`` object from a
        ``polars.DataFrame`` containing the ranking.

        Internally, ``RankedVote`` uses a compressed DataFrame with
        the number of occurrences for each ranking. For example if the
        same ranking is ``N`` times in the DataFrame, it will be
        re-encoded as a single row with a count of ``N``.
        The "compressed" representation is more efficient because the
        new DataFrame can be much smaller.

        Args:
            ranking: The DataFrame with the ranking for each voter.
            count_col: The column that will contain the count values
                for each ranking.

        Example usage:

        ```pycon

        >>> import polars as pl
        >>> from votingsys.vote import RankedVote
        >>> vote = RankedVote.from_dataframe(
        ...     pl.DataFrame(
        ...         {"a": [0, 1, 2, 1, 0, 0], "b": [1, 2, 0, 2, 1, 1], "c": [2, 0, 1, 0, 2, 2]}
        ...     )
        ... )
        >>> vote
        RankedVote(num_candidates=3, num_voters=6, count_col='count')
        >>> vote.ranking
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
        return cls.from_dataframe_with_count(
            ranking=compute_count_aggregated_dataframe(ranking, count_col=count_col),
            count_col=count_col,
        )

    @classmethod
    def from_dataframe_with_count(
        cls, ranking: pl.DataFrame, count_col: str = "count"
    ) -> RankedVote:
        r"""Instantiate a ``RankedVote`` object from a
        ``polars.DataFrame`` containing the rankings and their
        associated counts.

        Args:
            ranking: A DataFrame with the ranking for each voters. Each
                column represents a candidate, and each row is a voter
                ranking. The ranking goes from ``0`` to ``n-1``, where
                ``n`` is the number of candidates. One column contains
                the number of voters for this ranking.
            count_col: The column with the count data for each ranking.

        Example usage:

        ```pycon

        >>> import polars as pl
        >>> from votingsys.vote import RankedVote
        >>> vote = RankedVote.from_dataframe_with_count(
        ...     pl.DataFrame(
        ...         {
        ...             "a": [0, 1, 2, 0, 2],
        ...             "b": [1, 2, 0, 1, 1],
        ...             "c": [2, 0, 1, 2, 0],
        ...             "count": [3, 5, 2, 1, 0],
        ...         }
        ...     ),
        ... )
        >>> vote
        RankedVote(num_candidates=3, num_voters=11, count_col='count')
        >>> vote.ranking
        shape: (3, 4)
        ┌─────┬─────┬─────┬───────┐
        │ a   ┆ b   ┆ c   ┆ count │
        │ --- ┆ --- ┆ --- ┆ ---   │
        │ i64 ┆ i64 ┆ i64 ┆ i64   │
        ╞═════╪═════╪═════╪═══════╡
        │ 1   ┆ 2   ┆ 0   ┆ 5     │
        │ 0   ┆ 1   ┆ 2   ┆ 4     │
        │ 2   ┆ 0   ┆ 1   ┆ 2     │
        └─────┴─────┴─────┴───────┘

        ```
        """
        cols = [count_col, *sorted([col for col in ranking.columns if col != count_col])]
        return cls(
            ranking=remove_zero_weight_rows(
                sum_weights_by_group(ranking, weight_col=count_col), weight_col=count_col
            ).sort(by=cols, descending=True),
            count_col=count_col,
        )


def compute_borda_count(
    ranking: pl.DataFrame, points: Sequence[float], count_col: str
) -> dict[str, float]:
    r"""Compute the Borda count given the rankings and the points per
    rank.

    The Borda count method is a ranked voting system where voters
    list candidates in order of preference. Points are assigned
    based on position in each ranking. For example, in an election
    with n candidates, a first-place vote earns n points, second
    place gets n-1, and so on, down to 1. The candidate with the
    highest total score across all votes wins. This method
    considers the overall preferences of voters, not just their
    top choices.

    Args:
        ranking: A DataFrame with the ranking for each voter. Each
            column represents a candidate, and each row is a voter
            ranking. The ranking goes from ``0`` to ``n-1``, where
            ``n`` is the number of candidates. One column contains
            the number of voters for this ranking.
        points: The points associated for each rank. The first value
            is the point for rank 0, the second value is the point
            for rank 1, etc. The number of points must be equal to
            the number of candidates.
        count_col: The column with the count data for each ranking.

    Returns:
        The Borda count for each candidate. The key is the candidate
            and the value is the Borda count.

    Raises:
        ValueError: if ``count_col`` does not exist in the DataFrame.
        ValueError: if the number of points is different from the number of candidates.

    Example usage:

    ```pycon

    >>> import polars as pl
    >>> from votingsys.vote.rank import compute_borda_count
    >>> counts = compute_borda_count(
    ...     ranking=pl.DataFrame(
    ...         {"a": [0, 1, 2], "b": [1, 2, 0], "c": [2, 0, 1], "count": [3, 5, 2]}
    ...     ),
    ...     points=[3, 2, 1],
    ...     count_col="count",
    ... )
    >>> counts
    {'a': 21.0, 'b': 17.0, 'c': 22.0}

    ```
    """
    check_column_exist(ranking, count_col)
    num_cands = ranking.shape[1] - 1
    if len(points) != num_cands:
        msg = (
            f"The number of points ({len(points):,}) is different from the number "
            f"of candidates ({num_cands:,})"
        )
        raise ValueError(msg)
    total = defaultdict(float)
    for rank, point in enumerate(points):
        counts = weighted_value_count(ranking, value=rank, weight_col=count_col)
        for key, val in counts.items():
            total[key] += val * point
    return dict(total)
