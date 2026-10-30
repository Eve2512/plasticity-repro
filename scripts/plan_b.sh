#!/bin/zsh
# Plan B, part 1 (approved by the user 2026-10-30): extend every lineage to checkpoint 10,
# and add a second Hex Haiku medium lineage (checkpoints 0-10, 8/12/4 games).
# Extended lineages reflect on their saved final checkpoint first (harness/runner.py _extend).
# --cap is the lineage's total, so it is the amount billed so far plus the approved extension.
# Two waves of at most 24 games at once, the load plan A ran with, so tool timings stay comparable.
# Each run retries with --resume after a crash (network errors), up to 5 times.
# Usage: scripts/plan_b.sh
cd "$(dirname "$0")/.." || exit 1
mkdir -p runs/logs

run() {  # name game model cap id reflect-effort(or -) resume(new|resume)
  local name=$1 game=$2 model=$3 cap=$4 id=$5 reflect=$6 mode=$7
  local args=(--game $game --model $model --effort medium --rounds 10
              --train 8 --id $id --ood 4 --workers 4 --cap $cap --name $name --yes)
  [ $reflect != - ] && args+=(--reflect-effort $reflect)
  [ $mode = resume ] && args+=(--resume)
  echo "plan B: $(date '+%F %T') ${args[*]}" >> runs/logs/$name.log
  local try=1
  uv run python scripts/run_hex.py $args >> runs/logs/$name.log 2>&1
  while [ $? -ne 0 ] && [ $try -lt 5 ]; do
    try=$((try + 1))
    echo "retry $try with --resume" >> runs/logs/$name.log
    uv run python scripts/run_hex.py ${args:#--resume} --resume >> runs/logs/$name.log 2>&1
  done
}

S=anthropic/claude-sonnet-5.5
H=anthropic/claude-haiku-5.5

# Wave 1: Go and Hex Haiku (as in plan A)
run go_sonnet_reflect_high      go  $S 22.50 20 high resume &
run go_sonnet_reflect_high_rep2 go  $S 18.10 20 high resume &
run go_haiku_reflect_high       go  $H  3.30 20 high resume &
run go_haiku_reflect_high_rep2  go  $H  3.10 20 high resume &
run hex_haiku_reflect_high      hex $H  2.50 12 high resume &
run hex_haiku_reflect_high_rep2 hex $H  2.60 12 high resume &
wait
echo "plan B wave 1 finished $(date '+%F %T')"

# Wave 2: Hex Sonnet, and the new Hex Haiku medium lineage
run lineage_a2                  hex $S 14.50 12 -    resume &
run sonnet_medium_rep2          hex $S 14.60 12 -    resume &
run sonnet_reflect_high         hex $S 11.00 12 high resume &
run sonnet_reflect_high_rep2    hex $S 11.30 12 high resume &
run hex_haiku_medium_rep2       hex $H  5.50 12 -    new    &
wait
echo "plan B wave 2 finished $(date '+%F %T')"
