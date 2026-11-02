#!/bin/zsh
# Raise the caps of the four GLM 5.3 lineages so they can reach checkpoint 10
# (approved by the user 2026-11-02: $14/$14/$10/$10 -> $18/$16/$18/$18, $70 in total).
# Nothing is restarted: each lineage keeps its run from scripts/plan_c_resume_glm.sh. When that
# run ends and the lineage has not reached checkpoint 10 (it stopped at its old cap), it is
# resumed here with the new cap. Each resume retries after a crash, up to 5 times.
# Usage: scripts/plan_c_glm_new_caps.sh
cd "$(dirname "$0")/.." || exit 1

running() {  # true while the lineage has a run, checked twice to bridge the gap between retries
  pgrep -f "run_hex.py.*--name $1 " > /dev/null && return 0
  sleep 15
  pgrep -f "run_hex.py.*--name $1 " > /dev/null
}

complete() {  # true once the lineage has checkpoints 0-10
  uv run python -c "import json, sys; sys.exit(len(json.load(open('runs/$1/results.json'))['checkpoints']) < 11)"
}

run() {  # name game cap
  local name=$1 game=$2 cap=$3 id=12
  [ $game = go ] && id=20
  while running $name; do sleep 60; done
  complete $name && return
  local args=(--game $game --model z-ai/glm-5.3 --effort medium --rounds 10 --train 8 --id $id --ood 4
              --workers 2 --cap $cap --name $name --yes --reflect-effort high --resume)
  echo "plan C GLM new cap: $(date '+%F %T') ${args[*]}" >> runs/logs/$name.log
  local try=1
  uv run python scripts/run_hex.py $args >> runs/logs/$name.log 2>&1
  while [ $? -ne 0 ] && [ $try -lt 5 ]; do
    try=$((try + 1))
    echo "retry $try with --resume" >> runs/logs/$name.log
    uv run python scripts/run_hex.py $args >> runs/logs/$name.log 2>&1
  done
}

run go_glm_reflect_high       go  18.00 &
run go_glm_reflect_high_rep2  go  16.00 &
run hex_glm_reflect_high      hex 18.00 &
run hex_glm_reflect_high_rep2 hex 18.00 &
wait
echo "plan C GLM new caps finished $(date '+%F %T')"
