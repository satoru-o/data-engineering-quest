"""quest-02: アクセスログの型そろえ。

書き換えるのは TODO の3行の右辺だけ。読み込みと書き出しは触らなくてよい。
書き方は ../../CHEATSHEET.md の「型を直す」「文字列」に全部載っている。

    mk quest-02        これを実行して判定する
"""

from pathlib import Path

import pandas as pd

# このファイルは work/ に配られて動く。skeleton/ や solution/ から直接動かしても
# 同じ場所を読み書きできるよう、クエストのディレクトリを基準に組み立てている
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "access_log.csv"
OUT = ROOT / "work" / "access_log.parquet"

df = pd.read_csv(SRC)

# 届いたそのままの姿。全部が文字列で入っていることを確認してから書く
print("--- 生データ ---")
print(df.head())

# TODO 1: ts を datetime64[ns, UTC] にする
#   いま: "2026-01-05T00:12:03Z" という文字列 (object)
#   末尾の Z は「UTC である」という意味。これを潰さずに型を付ける
df["ts"] = df["ts"]  # ← この右辺を書き換える

# TODO 2: status を Int64 にする ("-" は欠損として扱う)
#   いま: "200" や "-" が混ざっているので列ぜんぶが文字列 (object)
#   int64 ではなく Int64 (大文字) 。欠損を持てる整数型のほう
df["status"] = df["status"]  # ← この右辺を書き換える

# TODO 3: dur を「秒の float64」にする ("1.2s" -> 1.2)
#   いま: 数字のうしろに s が付いた文字列 (object)
df["dur"] = df["dur"]  # ← この右辺を書き換える

OUT.parent.mkdir(exist_ok=True)
df.to_parquet(OUT, index=False)

# 書けたところから型が変わっていく。ここが下の採点とそのまま対応している
print("--- いまの型 ---")
print(df.dtypes)
