#!/bin/bash
# 매일 정오: headless Claude가 PLAYBOOK.md대로 글 작성·발행·Facebook 포스팅까지 수행.
export PATH="/Users/pass4u/.local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
REPO="/Users/pass4u/VOXEN/auto_blog"
LOG="$REPO/logs/$(date '+%Y-%m-%d').log"
mkdir -p "$REPO/logs"

cd "$REPO" || exit 1
echo "==== $(date '+%F %T') 자동 발행 시작" >> "$LOG"

claude -p "$(cat PLAYBOOK.md)" \
  --allowedTools "Read Edit Write Glob Grep Bash(git *) Bash(python3 *) Bash(ls *)" \
  --permission-mode bypassPermissions \
  --output-format text \
  >> "$LOG" 2>&1

echo "==== $(date '+%F %T') 종료 (exit $?)" >> "$LOG"
