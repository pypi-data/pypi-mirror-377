# Data Representation

In preferential or ranked voting, each voter expresses an ordered list of preferences over a set of
candidates.
When representing this data in tabular form, there are multiple valid approaches, each suited to
different kinds of analysis.

Let's assume there are 4 candidates: `A`, `B`, `C`, and `D`.

## Ranking Position as Columns

One common approach is to use a "ranking-position as column" format.
In this structure, each row represents a voter, and each column corresponds to a ranking position (
e.g. first, second, third).
The cell values indicate the candidate ranked at that position.
This format directly shows each voter's preference order.

| count | rank_1 | rank_2 | rank_3 | rank_4 |
|-------|--------|--------|--------|--------|
|       | C      | A      | B      | D      |
|       |        |        |        |        |
|       |        |        |        |        |
|       |        |        |        |        |
|       |        |        |        |        |

**Appropriate use cases:**

- Implementing ranked voting rules such as Instant Runoff, Borda Count, or Top-k approval.
- Identifying the top-ranked candidate per voter.
- Grouping or counting identical ballots.
- Working with data that mirrors the structure of actual ballots.

**Limitations:**

- It is less efficient for analyses that require identifying the rank assigned to a specific
  candidate without reshaping the data.

## Candidate as Columns

An alternative approach is the "candidate as column" format, where each row also represents a voter,
but each column corresponds to a candidate, and the cell values indicate the rank assigned to that
candidate by the voter.
This format makes it easy to compare how each candidate was ranked across voters.

| count | A | B | C | D |
|-------|---|---|---|---|
|       | 1 | 2 | 0 | 3 |
|       |   |   |   |   |
|       |   |   |   |   |
|       |   |   |   |   |
|       |   |   |   |   |

**Appropriate use cases:**

- Analyzing rankings from the perspective of each candidate (e.g., average or median rank).
- Performing pairwise comparisons used in Condorcet methods.
- Computing how frequently a specific candidate appears in a given rank.
- Applying statistical or machine learning models where candidates are treated as variables.

**Limitations:**

- It may require reshaping the data to apply position-based voting rules.

## Comparison

Choosing the right tabular format for ranked voting data depends on the task.

| Task                                        | Recommended Format          |
|---------------------------------------------|-----------------------------|
| Implementing ranked-choice voting rules     | Ranking position as columns |
| Counting first-choice votes                 | Ranking position as columns |
| Computing statistics per candidate          | Candidate as columns        |
| Analyzing pairwise comparisons (Condorcet)  | Candidate as columns        |
| Grouping or aggregating identical ballots   | Ranking position as columns |
| Applying statistical models to ranking data | Candidate as columns        |
