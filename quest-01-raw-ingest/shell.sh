#!/bin/sh
# 作業用コンテナに入る。pandas / pyarrow / duckdb が入っている。
#   /data  生データ (読み取り専用)
#   /work  自分のコード (ホストの work/ と同じ)
#   /out   出力の置き場
set -e
cd "$(dirname "$0")"

if ! docker compose ps --status running --services 2>/dev/null | grep -qx tools; then
  echo "作業用コンテナが動いていません。先に ./setup.sh を実行してください。"
  exit 1
fi

exec docker compose exec tools bash
