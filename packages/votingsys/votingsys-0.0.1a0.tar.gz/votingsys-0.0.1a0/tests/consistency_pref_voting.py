"""Verify consistency with https://github.com/voting-tools/pref_voting/

TODO: rewrite as tests
"""

import logging

from pref_voting.profiles import Profile

logger = logging.getLogger(__name__)


def main() -> None:
    prof = Profile([[0, 1, 2], [1, 2, 0], [2, 0, 1]], rcounts=[3, 5, 2])
    # prof = Profile(
    #     [
    #         [1, 0, 2],
    #         [1, 2, 0],
    #         [0, 1, 2],
    #         [0, 2, 1],
    #         [2, 1, 0],
    #     ],
    #     rcounts=[3, 1, 4, 1, 9],
    #     cmap={0: "C", 1: "M", 2: "S"},
    # )
    prof.display()

    logger.info(f"The number of voters is {prof.num_voters}")
    logger.info(f"The number of candidate is {prof.num_cands}")
    logger.info(f"The candidates are {prof.candidates}")
    logger.info(f"rankings: {prof.rankings}")
    logger.info(f"ranks:\n{prof._ranks}\n")

    logger.info(f"The margin of 0 over 1 is {prof.margin(0, 1)}")
    logger.info(f"The margin of 1 over 0 is {prof.margin(1, 0)}")
    logger.info(f"The margin of 0 over 2 is {prof.margin(0, 2)}")
    logger.info(f"The margin of 2 over 0 is {prof.margin(2, 0)}")
    logger.info(f"The margin of 1 over 2 is {prof.margin(1, 2)}")
    logger.info(f"The margin of 2 over 1 is {prof.margin(2, 1)}\n")

    logger.info(f"0 is majority preferred over 1 is {prof.majority_prefers(0, 1)}")
    logger.info(f"0 is majority preferred over 2 is {prof.majority_prefers(0, 2)}")
    logger.info(f"1 is majority preferred over 2 is {prof.majority_prefers(1, 2)}\n")

    logger.info(f"The margin matrix for the profile is: {prof.margin_matrix}\n")

    logger.info(f"The Condorcet winner is {prof.condorcet_winner()}")
    logger.info(f"The Condorcet loser is {prof.condorcet_loser()}")
    logger.info(f"The weak Condorcet winner(s) is(are) {prof.weak_condorcet_winner()}\n")

    logger.info(f"The Plurality scores for the candidates are {prof.plurality_scores()}")
    logger.info(f"The Borda scores for the candidates are {prof.borda_scores()}")
    logger.info(f"The Copeland scores for the candidates are {prof.copeland_scores()}\n")

    for c1, c2 in [[0, 0], [0, 1], [0, 2], [1, 0], [1, 1], [1, 2], [2, 0], [2, 1], [2, 2]]:
        logger.info(f"The support of {c1} over {c2} is {prof.support(c1, c2)}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
