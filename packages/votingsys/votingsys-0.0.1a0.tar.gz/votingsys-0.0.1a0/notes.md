# Random Notes

## Data representation

- anonymous
- can have null values
- can have the same ranking

- Test with a lot of candidates

### DataFrame with the rank for each candidate

### DataFrame with the score for each candidate

- descending vs ascending

## Rule

- voter ranks candidates
- single vs multiple winners: https://en.wikipedia.org/wiki/Comparison_of_voting_rules
- Ballot type:
    - single mark
    - ranking
    - truncated ranking
    - ranking with ties
    - rating
- approval and score voting: https://en.wikipedia.org/wiki/Approval_voting
- approve or disapprove of candidates, or decide to express no opinion
- Score each candidate by filling in a number (0 is worst; 9 is best)
- Majority Rule: This concept means that the candidate (choice) receiving more than 50%
  of the vote is the winner.

Raw Ranking

| rank_1 | rank_2 | rank_3 |
|--------|--------|--------|
| B      | A      | C      |
| B      | A      | C      |
| B      | A      | C      |
| B      | A      | C      |
| B      | A      | C      |
| A      | B      | C      |
| A      | B      | C      |
| C      | B      | A      |
| C      | B      | A      |
| C      | B      | A      |
| C      | B      | A      |
| C      | B      | A      |
| C      | B      | A      |
| C      | B      | A      |

Ranking

| count | rank_1 | rank_2 | rank_3 |
|-------|--------|--------|--------|
| 5     | B      | A      | C      |
| 2     | A      | B      | C      |
| 7     | C      | B      | A      |

Preference

| count | A | B | C |
|-------|---|---|---|
| 5     | 1 | 0 | 2 |
| 2     | 0 | 1 | 2 |
| 7     | 2 | 1 | 0 |

Preference with ties

| count | A | B | C |
|-------|---|---|---|
| 5     | 1 | 0 | 1 |
| 2     | 0 | 1 | 2 |
| 7     | 0 | 1 | 0 |

Truncated/partial Preference

| count | A | B | C | D |
|-------|---|---|---|---|
| 5     | 1 | 0 |   | 2 |
| 2     | 0 |   | 2 | 1 |
| 7     | 2 | 1 | 0 |   |
