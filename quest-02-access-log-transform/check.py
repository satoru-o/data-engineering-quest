"""quest-02 の判定。work/access_log.parquet を見て3問ぶんの結果を出す。

quest-01 の checker とは作りが違う。あちらは常駐して10秒ごとに出力を見張り、
最初の失敗で打ち切って FLAG を出す。こちらは:

  - 常駐しない。1回走って終わる (mk quest-02 が solve.py の直後に呼ぶ)
  - 最初の失敗で打ち切らない。1問1TODO なので、3問すべて判定して部分点を見せる
  - FLAG は出さない。15分で終わる問題に隠し玉は要らない

正解の値は data/access_log.csv から標準ライブラリだけで組み立てている。
pandas の書き方 (= 答えそのもの) がこのファイルに出てこないようにするためと、
CSV を差し替えても期待値を書き直さなくて済むようにするため。
"""

import csv
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "data" / "access_log.csv"
OUT = ROOT / "work" / "access_log.parquet"

# 見出しに続くドットを揃える幅 (半角換算)
LABEL_W = 46


def width(s: str) -> int:
    """端末に表示したときの桁数。全角は2桁として数える。

    len() は文字数なので、日本語混じりの見出しでは実際の見た目とずれる。
    ドットの並びが揃わないだけの話だが、揃っていないと結果が読みにくい
    """
    return sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in s)


def load_raw() -> list[dict[str, str]]:
    with SRC.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def expected_ts(raw: list[dict[str, str]]) -> list[datetime]:
    return [
        datetime.strptime(r["ts"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        for r in raw
    ]


def expected_status(raw: list[dict[str, str]]) -> list[int | None]:
    return [None if r["status"] == "-" else int(r["status"]) for r in raw]


def expected_dur(raw: list[dict[str, str]]) -> list[float]:
    return [float(r["dur"].removesuffix("s")) for r in raw]


def fmt(v: object) -> str:
    """値を人が読める形にする。datetime の repr は長すぎて比較にならない。"""
    if isinstance(v, datetime):
        return str(v)
    return repr(v)


def judge(series: pd.Series, want_dtype: str, want_values: list) -> str | None:
    """合っていれば None、間違っていれば理由の文字列を返す。"""
    if str(series.dtype) != want_dtype:
        return f"期待 dtype: {want_dtype}   実際: {series.dtype}"

    got = [None if pd.isna(v) else v for v in series.tolist()]
    for i, (g, w) in enumerate(zip(got, want_values)):
        if g == w:
            continue
        # float は表記のゆれではなく値で見る
        if isinstance(g, float) and isinstance(w, float) and abs(g - w) < 1e-9:
            continue
        return f"{i + 2}行目の値が違う   期待: {fmt(w)}   実際: {fmt(g)}"
    return None


def main() -> int:
    if not OUT.exists():
        print(f"{OUT} がない。先に work/solve.py を動かすこと")
        return 1

    raw = load_raw()
    df = pd.read_parquet(OUT)

    # 列を消したり行を絞ったりするクエストではない。先に土台を見る
    if list(df.columns) != ["ts", "path", "status", "dur"]:
        print(f"列が変わっている   期待: ['ts', 'path', 'status', 'dur']   実際: {list(df.columns)}")
        return 1
    if len(df) != len(raw):
        print(f"行数が変わっている   期待: {len(raw)}   実際: {len(df)}")
        return 1

    questions = [
        ("問1  ts を datetime64[ns, UTC] に", "ts", "datetime64[ns, UTC]", expected_ts(raw), "型を直す"),
        ("問2  status を Int64 に", "status", "Int64", expected_status(raw), "型を直す"),
        ("問3  dur を秒の float64 に", "dur", "float64", expected_dur(raw), "文字列"),
    ]

    passed = 0
    print()
    for label, column, want_dtype, want_values, section in questions:
        reason = judge(df[column], want_dtype, want_values)
        dots = "." * max(3, LABEL_W - width(label))
        if reason is None:
            passed += 1
            print(f"{label} {dots} OK")
        else:
            print(f"{label} {dots} NG")
            print(f"       {reason}")
            print(f"       CHEATSHEET.md の「{section}」を見ること")
    print()

    if passed == len(questions):
        print("--------------------------------------------------------")
        print("  全問正解。アクセスログが集計できる型になった")
        print("  次は quest-01 で、仕様書だけから同じことを組み立てる")
        print("--------------------------------------------------------")
        return 0

    print(f"{len(questions)}問中 {passed}問。work/solve.py を直してもう一度 mk quest-02")
    return 1


if __name__ == "__main__":
    sys.exit(main())
