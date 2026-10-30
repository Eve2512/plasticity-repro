#!/bin/zsh
# Plan C (approved by the user 2026-10-30), checkpoints 0-10, actor effort medium:
# - Go at reflection effort medium: two lineages each of Sonnet 5.5 and Haiku 5.5;
# - GLM 5.3 (harness/chat_model.py) at reflection effort high: two lineages each on Hex and Go.
# Games per checkpoint as in the other runs: Hex 8/12/4, Go 8/20/4.
# Starts once plan B has finished, so at most 24 games run at once, as in plans A and B,
# and once the account has $98 left (the caps' total).
# A run that meets an empty account stops cleanly (HTTP 402) and can be resumed later.
# Each run retries with --resume after a crash (network errors), up to 5 times.
# Usage: scripts/plan_c.sh
cd "$(dirname "$0")/.." || exit 1
mkdir -p runs/logs

while pgrep -f scripts/plan_b.sh > /dev/null; do sleep 60; done
# The caps add up to $98; wait until the account can cover them.
uv run python scripts/wait_for_credit.py 98 || exit 1
echo "plan C started $(date '+%F %T')"

run() {  # name game model cap reflect-effort(or -) workers
  local name=$1 game=$2 model=$3 cap=$4 reflect=$5 workers=$6 id=12
  [ $game = go ] && id=20
  local args=(--game $game --model $model --effort medium --rounds 10
              --train 8 --id $id --ood 4 --workers $workers --cap $cap --name $name --yes)
  [ $reflect != - ] && args+=(--reflect-effort $reflect)
  echo "plan C: $(date '+%F %T') ${args[*]}" >> runs/logs/$name.log
  local try=1
  uv run python scripts/run_hex.py $args >> runs/logs/$name.log 2>&1
  while [ $? -ne 0 ] && [ $try -lt 5 ]; do
    try=$((try + 1))
    echo "retry $try with --resume" >> runs/logs/$name.log
    uv run python scripts/run_hex.py $args --resume >> runs/logs/$name.log 2>&1
  done
}

run go_sonnet_medium      go  anthropic/claude-sonnet-5.5 21.00 -    4 &
run go_sonnet_medium_rep2 go  anthropic/claude-sonnet-5.5 21.00 -    4 &
run go_haiku_medium       go  anthropic/claude-haiku-5.5   4.00 -    4 &
run go_haiku_medium_rep2  go  anthropic/claude-haiku-5.5   4.00 -    4 &
run go_glm_reflect_high       go  z-ai/glm-5.3 14.00 high 2 &
run go_glm_reflect_high_rep2  go  z-ai/glm-5.3 14.00 high 2 &
run hex_glm_reflect_high      hex z-ai/glm-5.3 10.00 high 2 &
run hex_glm_reflect_high_rep2 hex z-ai/glm-5.3 10.00 high 2 &
wait
echo "plan C finished $(date '+%F %T')"
