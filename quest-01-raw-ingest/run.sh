#!/bin/sh
# work/ingest.py を作業用コンテナの中で実行する。
# 引数を渡すとそれを実行する:  ./run.sh python other.py  /  ./run.sh duckdb
set -e
cd "$(dirname "$0")"

if ! docker compose ps --status running --services 2>/dev/null | grep -qx tools; then
  echo "作業用コンテナが動いていません。先に ./setup.sh を実行してください。"
  exit 1
fi

if [ $# -eq 0 ]; then
  set -- python /work/ingest.py
fi

docker compose exec -T tools "$@"
