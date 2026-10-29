# 17 Artifact ablation (limitation test 6)

Held-out ID games from each lineage's final checkpoint, 24 per arm, same model, effort, openings
and opponents as the run. `with`: final inventory; `empty`: empty inventory; `forced`: final inventory
and the actor is told to load and use its tools. Tool use counts games that call an active entrypoint.

| Lineage | Checkpoint | Arm | Held-out ID | Lost to limits | Games calling a saved tool |
|---|---|---|---|---|---|
| `sonnet_reflect_high` | 7 | with | 22/24 = 92 % | 0 | 24 |
| `sonnet_reflect_high` | 7 | empty | 13/24 = 54 % | 0 | 0 |
| `sonnet_reflect_high` | 7 | forced | 22/24 = 92 % | 0 | 24 |
| `sonnet_reflect_high_rep2` | 7 | with | 22/24 = 92 % | 0 | 24 |
| `sonnet_reflect_high_rep2` | 7 | empty | 12/24 = 50 % | 0 | 0 |
| `sonnet_reflect_high_rep2` | 7 | forced | 20/24 = 83 % | 0 | 24 |
