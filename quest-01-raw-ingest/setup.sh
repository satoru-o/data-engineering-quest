#!/bin/sh
# 生データを作り直し、見張り役を起動する。
# 何度でも叩いてよい。叩くたびに生データもFLAGも作り直される。
set -e
cd "$(dirname "$0")"

printf 'HOST_UID=%s\nHOST_GID=%s\n' "$(id -u)" "$(id -g)" > .env

mkdir -p data out work

# 雛形を配る。既に自分で書いたものがあれば絶対に上書きしない。
# work/ はgit管理外なので、答えがコミットされる事故は起きない
for f in skeleton/*; do
  base=$(basename "$f")
  if [ ! -e "work/$base" ]; then
    cp "$f" "work/$base"
    echo "雛形を配置しました: work/$base"
  fi
done

echo "前の状態を片付けています..."
docker compose down -v > /dev/null 2>&1 || true
rm -f data/*.csv out/orders.parquet out/flag.txt out/report.txt 2>/dev/null || true

echo "イメージを用意しています... (初回は数分かかる)"
docker compose build > /dev/null

echo "生データを作り、見張り役を起動しています..."
docker compose up -d > /dev/null

i=0
while [ "$i" -lt 60 ]; do
  if [ -f out/report.txt ]; then
    break
  fi
  i=$((i + 1))
  sleep 1
done

if [ ! -f out/report.txt ]; then
  echo "NG: 見張り役が起動しませんでした。docker compose logs checker を見てください。"
  exit 1
fi

cat <<'EOF'

--------------------------------------------------------------------
生データが data/ に届いた。

EOF
ls -la data/*.csv | sed 's/^/  /'
cat <<'EOF'

出力の仕様は spec/orders.md にある。
仕様どおりの out/orders.parquet を作ること。

  ./shell.sh              作業用コンテナに入る (pandas / pyarrow / duckdb 入り)
  ./run.sh                work/ingest.py を実行する
  ./verify.sh --status    見張り役の判定結果を見る

見張り役は10秒ごとに出力を検証している。
すべて合格している間だけ out/flag.txt が現れる。

  cat out/flag.txt
  ./verify.sh 'FLAG{...}'
--------------------------------------------------------------------
EOF
