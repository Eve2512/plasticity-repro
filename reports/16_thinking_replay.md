# 16 Thinking replay of past reflections

Each saved reflection turn was sent again with the same context and `display: "summarized"`
(scripts/replay_thinking.py). The summary is a new sample on identical input, not the original
reasoning. "Same call" = the replayed turn makes exactly the recorded Bash calls (or none).

| Run | Reflection effort | Turns replayed | Same call | Turns with a summary | Mean summary length (chars) |
|---|---|---|---|---|---|
| `smoke_anthropic_claude-sonnet-5.5` | medium | 14 | 21 % | 43 % | 266 |
| `lineage_a` | medium | 4 | 75 % | 0 % | 0 |
| `lineage_a2` | medium | 45 | 29 % | 11 % | 245 |
| `sonnet_medium_rep2` | medium | 43 | 40 % | 14 % | 332 |
| `sonnet_reflect_high` | high | 72 | 18 % | 68 % | 573 |
| `sonnet_reflect_high_rep2` | high | 56 | 21 % | 52 % | 445 |
| `haiku_r20` | medium | 306 | 8 % | 98 % | 675 |
| `hex_haiku_reflect_high` | high | 154 | 5 % | 100 % | 2522 |
| `hex_haiku_reflect_high_rep2` | high | 136 | 7 % | 96 % | 1768 |
| `go_haiku_reflect_high` | high | 158 | 5 % | 99 % | 2141 |
| `go_haiku_reflect_high_rep2` | high | 138 | 7 % | 99 % | 2114 |
