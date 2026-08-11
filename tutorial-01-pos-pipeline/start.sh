#!/bin/sh
# JupyterLab を起動する。
#
#   ./start.sh              起動する (無い分だけノートブックを配る)
#   ./start.sh --reset      ノートブックを配り直す (自分の書き込みは失われる)
set -e
cd "$(dirname "$0")"

printf 'HOST_UID=%s\nHOST_GID=%s\n' "$(id -u)" "$(id -g)" > .env
mkdir -p work

for f in notebooks/*.ipynb; do
  base=$(basename "$f")
  if [ "$1" = "--reset" ] || [ ! -e "work/$base" ]; then
    cp "$f" "work/$base"
    echo "配置: work/$base"
  fi
done

echo "起動しています... (初回は数分かかる)"
docker compose up -d --build > /dev/null 2>&1

i=0
while [ "$i" -lt 60 ]; do
  if curl -sf -o /dev/null http://localhost:8889/lab; then
    break
  fi
  i=$((i + 1))
  sleep 1
done

cat <<'EOF'

--------------------------------------------------------------------
  http://localhost:8889/lab

  work/    ノートブック (git管理外。ここに書き込む)
  /data    POSの生データ (読み取り専用)

  01-ingest.ipynb から順に開いてください。

  止めるとき      ./stop.sh
  配り直すとき    ./start.sh --reset
--------------------------------------------------------------------
EOF
