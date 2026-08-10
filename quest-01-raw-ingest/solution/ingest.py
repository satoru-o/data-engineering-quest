#!/usr/bin/env python3
# ============================================================================
#  参考解答 (ネタバレ)
#
#  spec/orders.md の処理1〜6に、そのまま1ブロックずつ対応させてある。
#  写経しても身に付かないので、読んだあとは work/ingest.py で
#  自分の手で書き直すこと。
#
#  実行:  ./run.sh python /solution/ingest.py
# ============================================================================
import glob
import re
import unicodedata

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

DATA = "/data"
OUT = "/out/orders.parquet"

SCHEMA = pa.schema([
    ("order_id", pa.string()),
    ("order_date", pa.date32()),
    ("customer_name", pa.string()),
    ("region", pa.string()),
    ("status", pa.string()),
    ("quantity", pa.int32()),
    ("amount_jpy", pa.int64()),
])

# 仕様2. 欠損として扱う値
NULLISH = {"NULL", "N/A", "-", ""}


# --- 仕様1. すべてのファイルを結合する ------------------------------------
def read_csv_any(path):
    """文字コードを決め打ちしない。読めた方を採用する。

    errors="ignore" で握りつぶしてはいけない。例外は消えるが顧客名が壊れ、
    「止まる障害」が「黙る障害」に変わる。
    """
    for enc in ("utf-8", "cp932"):
        try:
            return pd.read_csv(path, dtype=str, keep_default_na=False, encoding=enc)
        except UnicodeDecodeError:
            continue
    raise RuntimeError(f"文字コードが判定できない: {path}")


def read_all():
    # dtype=str  … 型を推測させない。推測は汚れを勝手に埋めてしまう
    # keep_default_na=False … "NULL" などを pandas に勝手に NaN 化させない。
    #                          欠損の判定は仕様2で自分でやる
    frames = []
    for path in sorted(glob.glob(f"{DATA}/*.csv")):
        df = read_csv_any(path)
        df["_src"] = path.split("/")[-1]      # 診断用。最後に落とす
        print(f"  読み込み {path}: {len(df)} 行")
        frames.append(df)
    # 列名で揃うので、ファイルごとに列の並びが違っても問題ない
    return pd.concat(frames, ignore_index=True)


# --- 仕様2〜3. 欠損の正規化と表記ゆれの吸収 --------------------------------
def norm(s):
    """全セル共通の下ごしらえ。NFKC → strip → 欠損判定。

    NFKC で全角数字・全角記号・全角空白がまとめて半角側に寄る。
    個別に replace すると必ず漏れる。
    """
    if s is None:
        return None
    s = unicodedata.normalize("NFKC", str(s)).strip()
    return None if s in NULLISH else s


def parse_date(s):
    """2024-01-05 / 2024/01/05 / 2024年1月5日 の3通りを1本の正規表現で受ける。

    区切りが違うだけで構造は同じ。月日はゼロ詰めされていないことがある。
    """
    if s is None:
        return None
    m = re.fullmatch(r"(\d{4})[-/年](\d{1,2})[-/月](\d{1,2})日?", s)
    if not m:
        raise ValueError(f"日付が読めない: {s!r}")   # 黙って null にしない
    y, mo, d = (int(x) for x in m.groups())
    return pd.Timestamp(y, mo, d).date()             # date32 は date で作る


def parse_amount(s):
    """1200 / 1,200 / ¥1,200 / 1,200円 / 1200.0 を int にする。

    NFKC 済みなので ￥(全角) は ¥ に寄っている。
    "1200.0" があるので int(s) では落ちる。float を経由する。
    """
    if s is None:
        return None
    return int(float(re.sub(r"[¥,円]", "", s)))


def parse_qty(s):
    if s is None:
        return None
    return int(float(s))


# --- 本体 ------------------------------------------------------------------
def clean(df):
    def step(name, df):
        print(f"  {name:16s} {len(df):5d} 行")
        return df

    step("結合直後", df)

    # 2. 全セルに下ごしらえを通す
    for c in df.columns:
        df[c] = df[c].map(norm)

    # 3. 型ごとの解釈。amount → amount_jpy への改名もここ
    df["order_date"] = df["order_date"].map(parse_date)
    df["amount_jpy"] = df["amount"].map(parse_amount)
    df["quantity"] = df["quantity"].map(parse_qty)
    df["region"] = df["region"].str.lower()
    df["status"] = df["status"].str.lower()
    step("表記ゆれ吸収", df)

    # 4. 重複排除。order_id ごとに ingested_at が最新の1行
    #
    #    groupby().last() は「最後の行」ではなく「列ごとの最後の非null値」を返す。
    #    最新行の amount が欠損だと古い行の値を拾い、どの行にも存在しない
    #    キメラができる。行そのものを選ぶ drop_duplicates を使う。
    df = df.sort_values("ingested_at").drop_duplicates(subset="order_id", keep="last")
    step("重複排除", df)

    # 5. 除外。必ず4のあと。
    #    先に捨てると、訂正で無効になった注文が古い行のまま生き残る
    df = df[df["order_date"].notna()
            & df["amount_jpy"].notna()
            & df["quantity"].notna()
            & (df["quantity"] > 0)]
    step("除外", df)

    # 6. 列を仕様の順に絞って、order_id 昇順
    df = df[["order_id", "order_date", "customer_name", "region",
             "status", "quantity", "amount_jpy"]]
    df = df.sort_values("order_id").reset_index(drop=True)

    # 欠損が無くなってから型を固める。欠損があると int32 にできない
    df["quantity"] = df["quantity"].astype("int32")
    df["amount_jpy"] = df["amount_jpy"].astype("int64")
    return df


def main():
    df = clean(read_all())
    # スキーマを強制する。合わなければここで例外。取りこぼした汚れを
    # 「黙る障害」ではなく「止まる障害」にするための最後の関門
    pq.write_table(pa.Table.from_pandas(df, schema=SCHEMA, preserve_index=False), OUT)
    print(f"書き出し {OUT}: {len(df)} 行")


if __name__ == "__main__":
    main()
