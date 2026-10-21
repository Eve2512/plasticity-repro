# 08 Opening controls

Same openings and opponents as the smoke run (report 07). Win = 1.
Distance = empty cells each side still needs to connect, at the start position.

| Game | Actor | Distance (actor / opponent) | First legal action | Engine, 100k nodes |
|---|---|---|---|---|
| train g1 | red | 3 / 3 | 0 | 1 |
| train g2 | red | 4 / 4 | 0 | 1 |
| train g3 | blue | 4 / 3 | 0 | 1 |
| train g4 | blue | 4 / 3 | 0 | 1 |
| id g1 | red | 2 / 2 | 0 | 1 |
| id g2 | red | 4 / 3 | 0 | 1 |
| id g3 | blue | 3 / 3 | 0 | 0 |
| id g4 | blue | 4 / 3 | 0 | 0 |
| ood g1 | red | 3 / 4 | 0 | 1 |
| ood g2 | blue | 4 / 3 | 0 | 0 |

First legal action: 0/10. Engine: 7/10 (as blue: 2/5).

The weak and strong players get different results, so play decides these games and
an agent has room to improve between them. Blue openings (11 plies, opponent one stone
ahead) are harder: even the engine loses most of them.
