from __future__ import annotations

import polars as pl
import pytest
from coola import objects_are_equal

from votingsys.vote import (
    MultipleWinnersFoundError,
    RankedVote,
    WinnerNotFoundError,
)
from votingsys.vote.rank import compute_borda_count

################################
#     Tests for RankedVote     #
################################


@pytest.fixture
def ranking() -> pl.DataFrame:
    return pl.DataFrame({"a": [0, 1, 2], "b": [1, 2, 0], "c": [2, 0, 1], "count": [3, 5, 2]})


def test_ranked_vote_init_missing_count_col(ranking: pl.DataFrame) -> None:
    with pytest.raises(ValueError, match=r"column 'missing' is missing in the DataFrame:"):
        RankedVote(ranking, count_col="missing")


def test_ranked_vote_ranking(ranking: pl.DataFrame) -> None:
    assert objects_are_equal(
        RankedVote(ranking).ranking,
        pl.DataFrame({"a": [0, 1, 2], "b": [1, 2, 0], "c": [2, 0, 1], "count": [3, 5, 2]}),
    )


def test_ranked_vote_repr(ranking: pl.DataFrame) -> None:
    assert repr(RankedVote(ranking)).startswith("RankedVote(")


def test_ranked_vote_str(ranking: pl.DataFrame) -> None:
    assert str(RankedVote(ranking)).startswith("RankedVote(")


def test_ranked_vote_equal_true(ranking: pl.DataFrame) -> None:
    assert RankedVote(ranking).equal(RankedVote(ranking))


def test_ranked_vote_equal_false_different_ranking() -> None:
    assert not RankedVote(
        pl.DataFrame({"a": [0, 1, 2], "b": [1, 2, 0], "c": [2, 0, 1], "count": [3, 5, 2]})
    ).equal(
        RankedVote(
            pl.DataFrame({"a": [0, 1, 2], "b": [1, 2, 0], "c": [2, 0, 1], "count": [2, 1, 3]})
        )
    )


def test_ranked_vote_equal_false_different_type(ranking: pl.DataFrame) -> None:
    assert not RankedVote(ranking).equal(1)


def test_ranked_vote_get_num_candidates(ranking: pl.DataFrame) -> None:
    assert RankedVote(ranking).get_num_candidates() == 3


def test_ranked_vote_get_candidates(ranking: pl.DataFrame) -> None:
    assert objects_are_equal(RankedVote(ranking).get_candidates(), ("a", "b", "c"))


def test_ranked_vote_get_num_candidates_2() -> None:
    assert (
        RankedVote(
            pl.DataFrame(
                {
                    "a": [0, 1, 2, 3],
                    "b": [1, 2, 0, 2],
                    "c": [2, 0, 1, 1],
                    "d": [3, 3, 3, 0],
                    "count": [3, 5, 2, 1],
                }
            )
        ).get_num_candidates()
        == 4
    )


def test_ranked_vote_get_num_votes(ranking: pl.DataFrame) -> None:
    assert RankedVote(ranking).get_num_voters() == 10


def test_ranked_vote_get_num_voters_2() -> None:
    assert (
        RankedVote(
            pl.DataFrame(
                {
                    "a": [0, 1, 2, 3],
                    "b": [1, 2, 0, 2],
                    "c": [2, 0, 1, 1],
                    "d": [3, 3, 3, 0],
                    "count": [3, 5, 2, 1],
                }
            )
        ).get_num_voters()
        == 11
    )


def test_ranked_vote_absolute_majority_winner() -> None:
    assert (
        RankedVote(
            pl.DataFrame({"a": [0, 1, 2], "b": [1, 2, 0], "c": [2, 0, 1], "count": [3, 6, 2]})
        ).absolute_majority_winner()
        == "c"
    )


def test_ranked_vote_absolute_majority_winner_no_absolute_majority() -> None:
    with pytest.raises(WinnerNotFoundError, match=r"No winner found using absolute majority rule"):
        RankedVote(
            pl.DataFrame({"a": [0, 1, 2], "b": [1, 2, 0], "c": [2, 0, 1], "count": [3, 5, 2]})
        ).absolute_majority_winner()


def test_ranked_vote_absolute_majority_winner_no_majority() -> None:
    with pytest.raises(WinnerNotFoundError, match=r"No winner found using absolute majority rule"):
        RankedVote(
            pl.DataFrame({"a": [0, 1, 2], "b": [1, 2, 0], "c": [2, 0, 1], "count": [3, 4, 2]})
        ).absolute_majority_winner()


def test_ranked_vote_borda_counts(ranking: pl.DataFrame) -> None:
    assert objects_are_equal(
        RankedVote(ranking).borda_counts(),
        {"a": 21.0, "b": 17.0, "c": 22.0},
    )


def test_ranked_vote_borda_counts_custom_points(ranking: pl.DataFrame) -> None:
    assert objects_are_equal(
        RankedVote(ranking).borda_counts(points=[4, 2, 1]),
        {"a": 24.0, "b": 19.0, "c": 27.0},
    )


def test_ranked_vote_borda_counts_incorrect_points(ranking: pl.DataFrame) -> None:
    vote = RankedVote(ranking)
    with pytest.raises(
        ValueError,
        match=r"The number of points \(2\) is different from the number of candidates \(3\)",
    ):
        vote.borda_counts(points=[4, 2])


def test_ranked_vote_borda_count_winner(ranking: pl.DataFrame) -> None:
    assert RankedVote(ranking).borda_count_winner() == "c"


def test_ranked_vote_borda_count_winner_multiple() -> None:
    vote = RankedVote(
        pl.DataFrame({"a": [0, 1, 2], "b": [1, 2, 0], "c": [2, 0, 1], "count": [2, 2, 2]})
    )
    with pytest.raises(
        MultipleWinnersFoundError, match=r"Multiple winners found using Borda count rule:"
    ):
        vote.borda_count_winner()


def test_ranked_vote_borda_count_winner_one_candidate() -> None:
    assert RankedVote(pl.DataFrame({"a": [0], "count": [6]})).borda_count_winner() == "a"


def test_ranked_vote_borda_count_winner_custom_points(ranking: pl.DataFrame) -> None:
    assert RankedVote(ranking).borda_count_winner(points=[4, 2, 1]) == "c"


def test_ranked_vote_borda_count_winner_incorrect_points(ranking: pl.DataFrame) -> None:
    vote = RankedVote(ranking)
    with pytest.raises(
        ValueError,
        match=r"The number of points \(2\) is different from the number of candidates \(3\)",
    ):
        vote.borda_count_winner(points=[4, 2])


def test_ranked_vote_borda_count_winners(ranking: pl.DataFrame) -> None:
    assert RankedVote(ranking).borda_count_winners() == ("c",)


def test_ranked_vote_borda_count_winners_multiple() -> None:
    assert RankedVote(
        pl.DataFrame({"a": [0, 1, 2], "b": [1, 2, 0], "c": [2, 0, 1], "count": [2, 2, 2]})
    ).borda_count_winners() == ("a", "b", "c")


def test_ranked_vote_borda_count_winners_one_candidate() -> None:
    assert RankedVote(pl.DataFrame({"a": [0], "count": [6]})).borda_count_winners() == ("a",)


def test_ranked_vote_borda_count_winners_custom_points(ranking: pl.DataFrame) -> None:
    assert RankedVote(ranking).borda_count_winners(points=[4, 2, 1]) == ("c",)


def test_ranked_vote_borda_count_winners_incorrect_points(ranking: pl.DataFrame) -> None:
    vote = RankedVote(ranking)
    with pytest.raises(
        ValueError,
        match=r"The number of points \(2\) is different from the number of candidates \(3\)",
    ):
        vote.borda_count_winners(points=[4, 2])


def test_ranked_vote_plurality_counts(ranking: pl.DataFrame) -> None:
    assert objects_are_equal(
        RankedVote(ranking).plurality_counts(),
        {"a": 3, "b": 2, "c": 5},
    )


def test_ranked_vote_plurality_counts_one_candidate() -> None:
    assert objects_are_equal(
        RankedVote(pl.DataFrame({"a": [0, 0, 0], "count": [3, 6, 2]})).plurality_counts(),
        {"a": 11},
    )


def test_ranked_vote_plurality_winner(ranking: pl.DataFrame) -> None:
    assert RankedVote(ranking).plurality_winner() == "c"


def test_ranked_vote_plurality_winner_tie() -> None:
    vote = RankedVote(
        pl.DataFrame(
            {"a": [0, 1, 2, 1], "b": [1, 2, 0, 0], "c": [2, 0, 1, 2], "count": [3, 6, 2, 4]}
        )
    )
    with pytest.raises(
        MultipleWinnersFoundError, match=r"Multiple winners found using plurality rule:"
    ):
        vote.plurality_winner()


def test_ranked_vote_plurality_winner_1_candidate() -> None:
    assert RankedVote(pl.DataFrame({"a": [0], "count": [6]})).plurality_winner() == "a"


def test_ranked_vote_plurality_winners(ranking: pl.DataFrame) -> None:
    assert RankedVote(ranking).plurality_winners() == ("c",)


def test_ranked_vote_plurality_winners_multiple() -> None:
    assert RankedVote(
        pl.DataFrame(
            {"a": [0, 1, 2, 1], "b": [1, 2, 0, 0], "c": [2, 0, 1, 2], "count": [3, 6, 2, 4]}
        )
    ).plurality_winners() == ("b", "c")


def test_ranked_vote_plurality_winners_one_candidate() -> None:
    assert RankedVote(pl.DataFrame({"a": [0], "count": [6]})).plurality_winners() == ("a",)


def test_ranked_vote_from_dataframe() -> None:
    assert RankedVote.from_dataframe(
        pl.DataFrame(
            {
                "a": [0, 0, 0, 1, 1, 1, 1, 1, 2, 2],
                "b": [1, 1, 1, 2, 2, 2, 2, 2, 0, 0],
                "c": [2, 2, 2, 0, 0, 0, 0, 0, 1, 1],
            }
        )
    ).equal(
        RankedVote(
            pl.DataFrame({"a": [1, 0, 2], "b": [2, 1, 0], "c": [0, 2, 1], "count": [5, 3, 2]})
        )
    )


def test_ranked_vote_from_dataframe_count_col() -> None:
    assert RankedVote.from_dataframe(
        pl.DataFrame(
            {
                "a": [0, 0, 0, 1, 1, 1, 1, 1, 2, 2],
                "b": [1, 1, 1, 2, 2, 2, 2, 2, 0, 0],
                "c": [2, 2, 2, 0, 0, 0, 0, 0, 1, 1],
            }
        ),
        count_col="#n",
    ).equal(
        RankedVote(
            pl.DataFrame({"a": [1, 0, 2], "b": [2, 1, 0], "c": [0, 2, 1], "#n": [5, 3, 2]}),
            count_col="#n",
        )
    )


def test_ranked_vote_from_dataframe_count_col_exist() -> None:
    with pytest.raises(ValueError, match=r"column 'c' exists in the DataFrame:"):
        RankedVote.from_dataframe(
            pl.DataFrame(
                {
                    "a": [0, 0, 0, 1, 1, 1, 1, 1, 2, 2],
                    "b": [1, 1, 1, 2, 2, 2, 2, 2, 0, 0],
                    "c": [2, 2, 2, 0, 0, 0, 0, 0, 1, 1],
                }
            ),
            count_col="c",
        )


def test_ranked_vote_from_dataframe_with_count() -> None:
    assert RankedVote.from_dataframe_with_count(
        pl.DataFrame(
            {
                "a": [0, 1, 2, 0, 2],
                "b": [1, 2, 0, 1, 1],
                "c": [2, 0, 1, 2, 0],
                "count": [3, 5, 2, 1, 0],
            }
        ),
    ).equal(
        RankedVote(
            pl.DataFrame({"a": [1, 0, 2], "b": [2, 1, 0], "c": [0, 2, 1], "count": [5, 4, 2]})
        )
    )


def test_ranked_vote_from_dataframe_with_count_count_col() -> None:
    assert RankedVote.from_dataframe_with_count(
        pl.DataFrame(
            {
                "a": [0, 1, 2, 0, 2],
                "b": [1, 2, 0, 1, 1],
                "c": [2, 0, 1, 2, 0],
                "#n": [3, 5, 2, 1, 0],
            }
        ),
        count_col="#n",
    ).equal(
        RankedVote(
            pl.DataFrame({"a": [1, 0, 2], "b": [2, 1, 0], "c": [0, 2, 1], "#n": [5, 4, 2]}),
            count_col="#n",
        )
    )


#########################################
#     Tests for compute_borda_count     #
#########################################


def test_compute_borda_count(ranking: pl.DataFrame) -> None:
    assert objects_are_equal(
        compute_borda_count(ranking, points=[3, 2, 1], count_col="count"),
        {
            "a": 21.0,  # 9 + 10 + 2
            "b": 17.0,  # 6 + 5 + 6
            "c": 22.0,  # 15 + 4 + 3
        },
    )


def test_compute_borda_count_2(ranking: pl.DataFrame) -> None:
    assert objects_are_equal(
        compute_borda_count(ranking, points=[4, 2, 1], count_col="count"),
        {
            "a": 24.0,  # 12 + 10 + 2
            "b": 19.0,  # 8 + 5 + 6
            "c": 27.0,  # 20 + 4 + 3
        },
    )


def test_compute_borda_count_not_enough_points(ranking: pl.DataFrame) -> None:
    with pytest.raises(
        ValueError,
        match=r"The number of points \(2\) is different from the number of candidates \(3\)",
    ):
        compute_borda_count(ranking, points=[3, 1], count_col="count")


def test_compute_borda_count_too_many_points(ranking: pl.DataFrame) -> None:
    with pytest.raises(
        ValueError,
        match=r"The number of points \(4\) is different from the number of candidates \(3\)",
    ):
        compute_borda_count(ranking, points=[3, 2, 1, 0.5], count_col="count")


###################################################################################################
# Candy election example
# https://coconino.edu/resources/files/pdfs/academics/arts-and-sciences/MAT142/Chapter_7_VotingSystems.pdf
###################################################################################################


@pytest.fixture
def candy_election() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "C": [1, 2, 0, 0, 2],
            "M": [0, 0, 1, 2, 1],
            "S": [2, 1, 2, 1, 0],
            "count": [3, 1, 4, 1, 9],
        }
    )


@pytest.fixture
def candy_election_votes() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "C": [0, 2, 0, 1, 2, 2, 2, 2, 2, 1, 0, 1, 2, 2, 0, 0, 2, 2],
            "M": [2, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1],
            "S": [1, 1, 2, 2, 0, 0, 0, 0, 0, 2, 2, 2, 0, 0, 2, 2, 0, 0],
        }
    )


def test_candy_election_data_preparation(
    candy_election_votes: pl.DataFrame, candy_election: pl.DataFrame
) -> None:
    assert RankedVote.from_dataframe(candy_election_votes).equal(
        RankedVote.from_dataframe_with_count(candy_election)
    )


def test_candy_election_absolute_majority_winner(candy_election: pl.DataFrame) -> None:
    with pytest.raises(WinnerNotFoundError, match=r"No winner found using absolute majority rule"):
        RankedVote.from_dataframe_with_count(candy_election).absolute_majority_winner()


def test_candy_election_borda_counts(candy_election: pl.DataFrame) -> None:
    assert objects_are_equal(
        RankedVote(candy_election).borda_counts(), {"C": 31.0, "M": 39.0, "S": 38.0}
    )


def test_candy_election_borda_count_winner(candy_election: pl.DataFrame) -> None:
    assert RankedVote(candy_election).borda_count_winner() == "M"


def test_candy_election_plurality_counts(candy_election: pl.DataFrame) -> None:
    assert objects_are_equal(
        RankedVote(candy_election).plurality_counts(), {"C": 5, "M": 4, "S": 9}
    )


def test_candy_election_plurality_winner(candy_election: pl.DataFrame) -> None:
    assert RankedVote(candy_election).plurality_winner() == "S"
