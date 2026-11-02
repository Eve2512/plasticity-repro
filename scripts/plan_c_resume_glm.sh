#!/bin/zsh
# Resume the four GLM 5.3 lineages of plan C (scripts/plan_c.sh) with the same settings and caps.
# They stopped on 2026-11-02 when the OpenRouter key reached its own $200 limit (HTTP 403);
# the user raised the limit to $300 and approved the resume.
# Each run retries with --resume after a crash (network errors), up to 5 times.
# Usage: scripts/plan_c_resume_glm.sh
cd "$(dirname "$0")/.." || exit 1
echo "plan C GLM resume started $(date '+%F %T')"

run() {  # name game cap
  local name=$1 game=$2 cap=$3 id=12
  [ $game = go ] && id=20
  local args=(--game $game --model z-ai/glm-5.3 --effort medium --rounds 10 --train 8 --id $id --ood 4
              --workers 2 --cap $cap --name $name --yes --reflect-effort high --resume)
  echo "plan C GLM resume: $(date '+%F %T') ${args[*]}" >> runs/logs/$name.log
  local try=1
  uv run python scripts/run_hex.py $args >> runs/logs/$name.log 2>&1
  while [ $? -ne 0 ] && [ $try -lt 5 ]; do
    try=$((try + 1))
    echo "retry $try with --resume" >> runs/logs/$name.log
    uv run python scripts/run_hex.py $args >> runs/logs/$name.log 2>&1
  done
}

run go_glm_reflect_high       go  14.00 &
run go_glm_reflect_high_rep2  go  14.00 &
run hex_glm_reflect_high      hex 10.00 &
run hex_glm_reflect_high_rep2 hex 10.00 &
wait
echo "plan C GLM resume finished $(date '+%F %T')"
