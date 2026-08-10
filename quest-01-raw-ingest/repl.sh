#!/bin/sh
# 対話的に試すためのIPythonを起動する。データを読み込んだ状態から始まる。
#
#   df    data/ の全CSVを dtype=str で読んで結合したもの (文字コードは判定済み)
#   raw   ファイルごとのDataFrameの辞書
#
# 1行ずつ試して、動いた行だけを work/ingest.py に写していく、という進め方を想定している。
set -e
cd "$(dirname "$0")"

if ! docker compose ps --status running --services 2>/dev/null | grep -qx tools; then
  echo "作業用コンテナが動いていません。先に ./setup.sh を実行してください。"
  exit 1
fi

exec docker compose exec tools ipython -i /app/replstart.py
