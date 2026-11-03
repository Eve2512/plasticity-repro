#!/bin/zsh
# Plan D: the Hex Sonnet 5.5 effort comparison again, with held-out ID openings new at every
# checkpoint (--openings fresh, data/hex_openings_fresh_id.json), so no held-out game repeats
# (report 23). Two lineages at reflection effort high, two at medium (reflection effort as the
# actor's), every other setting as sonnet_reflect_high and lineage_a2: actor effort medium,
# checkpoints 0-10, 8 / 12 / 4 games per checkpoint, 4 games at a time per lineage.
# Training and OOD openings are the pooled banks of the original lineages.
# Caps from the originals' bills (high $10.05-11.06, medium $13.74-14.50) plus about 10 %.
# A run that meets an empty account stops cleanly (HTTP 402) and can be resumed later.
# Each run retries with --resume after a crash (network errors), up to 5 times.
# Usage: scripts/plan_d.sh
cd "$(dirname "$0")/.." || exit 1
mkdir -p runs/logs

run() {  # name cap reflect-effort(or -)
  local name=$1 cap=$2 reflect=$3
  local args=(--game hex --model anthropic/claude-sonnet-5.5 --effort medium --rounds 10 --openings fresh
              --train 8 --id 12 --ood 4 --workers 4 --cap $cap --name $name --yes)
  [ $reflect != - ] && args+=(--reflect-effort $reflect)
  echo "plan D: $(date '+%F %T') ${args[*]}" >> runs/logs/$name.log
  local try=1
  uv run python scripts/run_hex.py $args >> runs/logs/$name.log 2>&1
  while [ $? -ne 0 ] && [ $try -lt 5 ]; do
    try=$((try + 1))
    echo "retry $try with --resume" >> runs/logs/$name.log
    uv run python scripts/run_hex.py $args --resume >> runs/logs/$name.log 2>&1
  done
}

echo "plan D started $(date '+%F %T')"
run hex_sonnet_high_fresh        12.00 high &
run hex_sonnet_high_fresh_rep2   12.00 high &
run hex_sonnet_medium_fresh      15.50 -    &
run hex_sonnet_medium_fresh_rep2 15.50 -    &
wait
echo "plan D finished $(date '+%F %T')"
