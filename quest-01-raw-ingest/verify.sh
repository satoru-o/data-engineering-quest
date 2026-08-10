#!/bin/sh
# 出力が仕様を満たしているかを確認する。
#
#   ./verify.sh --status       見張り役の最新の判定結果を表示する
#   ./verify.sh 'FLAG{...}'    取得したFLAGを判定する
set -e
cd "$(dirname "$0")"

if [ ! -f out/report.txt ]; then
  echo "まだ見張り役が動いていません。./setup.sh を実行してください。"
  exit 1
fi

if [ "$1" = "--status" ] || [ -z "$1" ]; then
  cat out/report.txt
  if [ -z "$1" ]; then
    echo
    echo "答え合わせをするなら: ./verify.sh 'FLAG{取得した値}'"
  fi
  exit 0
fi

USER_FLAG="$1"

if [ ! -f out/flag.txt ]; then
  echo "NG: まだ out/flag.txt がありません。仕様を満たせていません。"
  echo
  cat out/report.txt
  exit 1
fi

AGE=$(( $(date +%s) - $(stat -c %Y out/flag.txt) ))
if [ "$AGE" -gt 45 ]; then
  echo "NG: FLAGが${AGE}秒前から更新されていません。今の出力は仕様を満たしていません。"
  echo
  cat out/report.txt
  exit 1
fi

ACTUAL=$(tr -d '\r\n' < out/flag.txt)

if [ "$USER_FLAG" = "$ACTUAL" ]; then
  echo "正解! $USER_FLAG"
  echo "  汚れた生データを、仕様どおりのテーブルに整形できました。"
  exit 0
else
  echo "不正解: そのFLAGは今動いている見張り役のものと一致しません。"
  echo "  (./setup.sh を叩き直すとFLAGは変わります)"
  exit 1
fi
