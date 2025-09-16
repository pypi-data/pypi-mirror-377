r"""Contain the vote implementations."""

from __future__ import annotations

__all__ = [
    "BaseVote",
    "MultipleWinnersFoundError",
    "RankedVote",
    "SingleMarkVote",
    "WinnerNotFoundError",
]

from votingsys.vote.base import (
    BaseVote,
    MultipleWinnersFoundError,
    WinnerNotFoundError,
)
from votingsys.vote.rank import RankedVote
from votingsys.vote.single_mark import SingleMarkVote
