#!/bin/zsh
# Plan A (reports/14_run_plan.md): six lineages, actor effort medium, reflection effort high,
# 7 rounds. Caps total $35 to fit the $36.58 left on the account (2026-10-27).
# Each run retries with --resume after a crash (network errors), up to 5 times.
# Usage: scripts/plan_a.sh     (needs the OpenRouter key limit raised above $50 + $35)
cd "$(dirname "$0")/.." || exit 1
mkdir -p runs/logs

run() {  # name game model cap train id ood workers
  local name=$1 game=$2 model=$3 cap=$4 train=$5 id=$6 ood=$7 workers=$8
  local args=(--game $game --model $model --effort medium --reflect-effort high --rounds 7
              --train $train --id $id --ood $ood --workers $workers --cap $cap --name $name --yes)
  local try=1
  uv run python scripts/run_hex.py $args >> runs/logs/$name.log 2>&1
  while [ $? -ne 0 ] && [ $try -lt 5 ]; do
    try=$((try + 1))
    echo "retry $try with --resume" >> runs/logs/$name.log
    uv run python scripts/run_hex.py $args --resume >> runs/logs/$name.log 2>&1
  done
}

run go_sonnet_reflect_high      go  anthropic/claude-sonnet-5.5 13.00 8 20 4 4 &
run go_sonnet_reflect_high_rep2 go  anthropic/claude-sonnet-5.5 13.00 8 20 4 4 &
run go_haiku_reflect_high       go  anthropic/claude-haiku-5.5   2.50 8 20 4 4 &
run go_haiku_reflect_high_rep2  go  anthropic/claude-haiku-5.5   2.50 8 20 4 4 &
run hex_haiku_reflect_high      hex anthropic/claude-haiku-5.5   2.00 8 12 4 4 &
run hex_haiku_reflect_high_rep2 hex anthropic/claude-haiku-5.5   2.00 8 12 4 4 &
wait
echo "plan A finished"
