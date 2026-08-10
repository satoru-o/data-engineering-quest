#!/usr/bin/env python3
"""
生データを仕様どおりに整形して out/orders.parquet を書く。

仕様は spec/orders.md にある。このファイルは骨組みだけなので、
今のまま実行すると見張り役に落とされる。out/report.txt を見ながら埋めていく。

  ../run.sh          このファイルを実行する (ホスト側から)
  ../shell.sh        コンテナに入って対話的にいじる

コンテナの中では:
  /data   生データ (読み取り専用)
  /out    出力先
pandas / pyarrow / duckdb が入っている。pandasで書いてもDuckDBのSQLで書いてもよい。
"""
import glob

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

DATA = "/data"
OUT = "/out/orders.parquet"

# 出力のスキーマ。ここは仕様どおりなので変えなくてよい
SCHEMA = pa.schema([
    ("order_id", pa.string()),
    ("order_date", pa.date32()),
    ("customer_name", pa.string()),
    ("region", pa.string()),
    ("status", pa.string()),
    ("quantity", pa.int32()),
    ("amount_jpy", pa.int64()),
])


def read_all():
    """data/ 配下のCSVを全部読んで1つのDataFrameにする。"""
    frames = []
    for path in sorted(glob.glob(f"{DATA}/*.csv")):
        # TODO: このファイル、本当にUTF-8で読めているか?
        #       読めたように見えて中身が壊れていることもある
        df = pd.read_csv(path, dtype=str, keep_default_na=False)
        print(f"  読み込み {path}: {len(df)} 行")
        frames.append(df)
    return pd.concat(frames, ignore_index=True)


def clean(df):
    """仕様 spec/orders.md の 2〜6 をここでやる。"""
    # TODO: 2. 欠損表現の正規化 (NULL / N/A / - / 空文字)
    # TODO: 3. 表記ゆれの吸収 (日付・金額・数量・地域・状態・顧客名)
    # TODO: 4. order_id ごとに ingested_at が最新の行だけ残す
    # TODO: 5. 除外 (4のあとで!)
    # TODO: 6. order_id 昇順
    return df


def main():
    df = read_all()
    print(f"結合後: {len(df)} 行")

    df = clean(df)
    print(f"整形後: {len(df)} 行")

    table = pa.Table.from_pandas(df, schema=SCHEMA, preserve_index=False)
    pq.write_table(table, OUT)
    print(f"書き出し {OUT}")


if __name__ == "__main__":
    main()
