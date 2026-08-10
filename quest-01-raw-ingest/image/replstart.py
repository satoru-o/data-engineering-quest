# ./repl.sh で IPython を起動したときに、最初に読み込まれるもの。
# よく使う import と、生データのパス一覧だけを用意する。
# (ここで整形まで済ませると練習にならないので、何もしない)
import glob
import re
import unicodedata

import duckdb
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

FILES = sorted(glob.glob("/data/*.csv"))

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 50)

print("使えるもの: pd / pa / pq / duckdb / unicodedata / re / glob")
print("FILES =")
for _f in FILES:
    print(f"  {_f}")
print("""
まずは1ファイル読んでみる:
    df = pd.read_csv(FILES[0], dtype=str, keep_default_na=False)
    df.head()

列にどんな値が入っているかを全部並べる (これが一番効く):
    sorted(df["quantity"].unique())

メソッド名を思い出せないとき:
    [m for m in dir(df) if "dup" in m]
    df.drop_duplicates?
""")
