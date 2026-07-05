#!/bin/bash
# PreToolUse Hook: 禁止在 main 分支 push
branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)
if [ "$branch" = "main" ] || [ "$branch" = "master" ]; then
  echo '{"decision": "deny", "message": "禁止直接推送 main/master 分支"}' >&1
  exit 2
fi
echo '{"decision": "allow"}' >&1
exit 0
