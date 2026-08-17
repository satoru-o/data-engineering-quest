"""quest-02 の参考解答。

skeleton/solve.py の TODO を埋めたもの。
自分で解く前に読むと一瞬で終わってしまうので、詰まってから開くこと。
"""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "access_log.csv"
OUT = ROOT / "work" / "access_log.parquet"

df = pd.read_csv(SRC)

print("--- 生データ ---")
print(df.head())

# TODO 1: ts を datetime64[ns, UTC] にする
# 末尾の Z は UTC を意味する。utc=True を付けると tz-aware になる
df["ts"] = pd.to_datetime(df["ts"], utc=True)

# TODO 2: status を Int64 にする ("-" は欠損)
# errors="coerce" で変換できない "-" が NaN になる。
# int64 ではなく Int64 (大文字) にすると欠損を持てる
df["status"] = pd.to_numeric(df["status"], errors="coerce").astype("Int64")

# TODO 3: dur を「秒の float64」にする ("1.2s" -> 1.2)
# 末尾の s を落としてから数値にする
df["dur"] = df["dur"].str.removesuffix("s").astype("float64")

OUT.parent.mkdir(exist_ok=True)
df.to_parquet(OUT, index=False)

print("--- いまの型 ---")
print(df.dtypes)
