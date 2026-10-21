# 09 Opening balance: contested vs legacy banks

Actor: 10,000-node engine (not used to build either bank), against the runner's
opponent for each slot. OOD: first 2 openings per colour only (1M nodes per move is slow).

| Bank | Split | Red wins | Blue wins | Actor moves per game (red / blue) |
|---|---|---|---|---|
| legacy | train | 14/20 | 9/20 | 4.6 / 5.2 |
| legacy | id | 16/20 | 11/20 | 4.5 / 4.7 |
| legacy | ood | 1/2 | 1/2 | 5.5 / 4.0 |
| contested | train | 13/20 | 16/20 | 6.0 / 6.0 |
| contested | id | 11/20 | 11/20 | 7.0 / 5.9 |
| contested | ood | 0/2 | 0/2 | 9.0 / 8.0 |

## Reading

Train and ID together (40 games per colour per bank):

| Bank | Red | Blue | Gap | z (two-proportion) |
|---|---|---|---|---|
| legacy | 30/40 = 75 % | 20/40 = 50 % | 25 points | about 2.3 |
| contested | 24/40 = 60 % | 27/40 = 68 % | −7 points | about −0.7 |

- **Colour balance:** the legacy banks favour red by 25 points; the contested banks
  show no significant gap.
- **Game length:** actor moves per game rise from 4.5–5.2 to 5.9–7.0 on train and ID,
  and to 8–9 in the OOD sample. More decisions per game give reflection more to work
  with; it also makes each game roughly 30 % more expensive in model calls.
- **Headroom:** the mid-strength engine wins 55–80 % of contested train and ID games, so
  a better or worse agent can still move the score in both directions.
- **OOD:** the sample (2 per colour) is too small to estimate balance; the mid engine
  lost all 4 contested OOD games against the 1M-node opponent.

Runs from here on use the contested banks (`RunConfig.openings = "contested"`).
Reports 05–08 were made with the legacy banks, and their scripts pin `source="legacy"`.
