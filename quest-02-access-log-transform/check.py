"""quest-02 の採点。work/solve.py を動かして ans1..ansN を見る。

quest-01 の checker とは作りが違う。あちらは常駐して10秒ごとに出力を見張り、
最初の失敗で打ち切って FLAG を出す。こちらは:

  - 常駐しない。1回走って終わる
  - 最初の失敗で打ち切らない。1問1TODO なので、全問判定して部分点を見せる
  - FLAG は出さない。15分で終わる問題に隠し玉は要らない

ファイルに書き出させて読み直す形は採っていない。答えが Series だったり
DataFrame だったりして直列化が合わないのと、CSV を挟むと dtype が消えるため。
runpy で solve.py を実行し、名前空間から ansN をそのまま受け取る。
"""

from __future__ import annotations

import json
import runpy
import sys
import unicodedata
from datetime import datetime
from pathlib import Path

import pandas as pd

import questions

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "data" / "access_log.csv"
SCREENS = ROOT / "data" / "screens.csv"
SOLVE = ROOT / "work" / "solve.py"
STATE = ROOT / "work" / ".quest.json"

# 見出しに続くドットを揃える幅 (半角換算)。
# 問題文は長いので見出しには入れず、落ちたときだけ下に添える。
# 節名さえ出ていれば、どのチートシートの節を引けばいいかは分かる
LABEL_W = 30


def width(s: str) -> int:
    """端末に表示したときの桁数。全角は2桁として数える。

    len() は文字数なので、日本語混じりの見出しでは実際の見た目とずれる。
    ドットの並びが揃わないだけの話だが、揃っていないと結果が読みにくい
    """
    return sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in s)


def fmt(v: object) -> str:
    """値を人が読める形にする。datetime の repr は長すぎて比較にならない。"""
    if isinstance(v, datetime):
        return str(v)
    return repr(v)


def norm(obj: object) -> object:
    """比べる前に添字をならす。

    DataFrame は添字を見ない。行を絞ったあとの添字は飛び飛びになるが、
    それは答えの一部ではないので、reset_index(drop=True) の付け忘れで
    落とすのは筋が悪い。

    Series は添字が RangeIndex のときだけ落とす。
    groupby の結果は添字 (path など) そのものが答えなので残す
    """
    if isinstance(obj, pd.DataFrame):
        return obj.reset_index(drop=True)
    if isinstance(obj, pd.Series) and isinstance(obj.index, pd.RangeIndex):
        return obj.reset_index(drop=True)
    return obj


def judge(got: object, want: object) -> str | None:
    """合っていれば None、間違っていれば理由の1行を返す。"""
    if got is ...:
        return "まだ書かれていない (ans が ... のまま)"

    if not isinstance(got, type(want)):
        return f"期待: {type(want).__name__}   実際: {type(got).__name__}"

    got, want = norm(got), norm(want)

    if isinstance(want, pd.DataFrame):
        if list(got.columns) != list(want.columns):
            return f"列が違う   期待: {list(want.columns)}   実際: {list(got.columns)}"
        if len(got) != len(want):
            return f"行数が違う   期待: {len(want)}行   実際: {len(got)}行"
        for col in want.columns:
            reason = compare_series(got[col], want[col])
            if reason:
                return f"列 {col} が違う   {reason}"
        return None

    if isinstance(want, pd.Series):
        if len(got) != len(want):
            return f"行数が違う   期待: {len(want)}行   実際: {len(got)}行"
        if not got.index.equals(want.index):
            return f"添字が違う   期待: {list(want.index)[:3]}...   実際: {list(got.index)[:3]}..."
        return compare_series(got, want)

    return None if got == want else f"期待: {fmt(want)}   実際: {fmt(got)}"


def compare_series(got: pd.Series, want: pd.Series) -> str | None:
    if str(got.dtype) != str(want.dtype):
        return f"dtype が違う   期待: {want.dtype}   実際: {got.dtype}"

    gv = [None if pd.isna(v) else v for v in got.tolist()]
    wv = [None if pd.isna(v) else v for v in want.tolist()]
    for i, (g, w) in enumerate(zip(gv, wv)):
        if g == w:
            continue
        # float は表記のゆれではなく値で見る
        if isinstance(g, float) and isinstance(w, float) and abs(g - w) < 1e-9:
            continue
        return f"{i + 1}件目の値が違う   期待: {fmt(w)}   実際: {fmt(g)}"
    return None


def load_raw() -> pd.DataFrame:
    """参照実装に渡す入力。solve.py が読むものと同じ CSV から作る。

    結合の問はマスタも要る。lambda の引数を1つに揃えたいので attrs に貼る
    """
    df = pd.read_csv(SRC)
    if SCREENS.exists():
        df.attrs["screens"] = pd.read_csv(SCREENS)
    return df


def main() -> int:
    if not STATE.exists() or not SOLVE.exists():
        print("問題がまだ配られていない。mk quest-02-new を叩くこと")
        return 1

    state = json.loads(STATE.read_text(encoding="utf-8"))
    seed = state["seed"]
    picked = [questions.BY_ID[i] for i in state["ids"]]

    # solve.py の中の print はそのまま出る。自分で仕込んだ確認も見える
    try:
        ns = runpy.run_path(str(SOLVE))
    except Exception as e:
        print(f"\nwork/solve.py が最後まで動かなかった: {type(e).__name__}: {e}")
        print("まず例外を消すこと。採点はそのあと")
        return 1

    raw = load_raw()

    passed = 0
    print()
    for i, q in enumerate(picked, start=1):
        label = f"問{i} [{q.section}]"
        got = ns.get(f"ans{i}", ...)
        reason = judge(got, q.solve(raw))
        dots = "." * max(3, LABEL_W - width(label))
        if reason is None:
            passed += 1
            print(f"{label} {dots} OK")
        else:
            print(f"{label} {dots} NG")
            print(f"       {q.ask}")
            print(f"       → {reason}")
            print(f"       CHEATSHEET.md の「{q.section}」を見ること")
    print()

    if passed == len(picked):
        print("--------------------------------------------------------")
        print(f"  全問正解 (seed={seed})")
        print("  別の3問を引くなら mk quest-02-new")
        print("--------------------------------------------------------")
        return 0

    print(
        f"{len(picked)}問中 {passed}問。work/solve.py を直してもう一度 mk quest-02"
        f"   (seed={seed})"
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
