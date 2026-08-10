#!/usr/bin/env python3
# ============================================================================
#  ネタバレ注意
#
#  このファイルは「汚れた生データの作り方」と「期待される出力の作り方」の
#  両方を持っている。読めばどこがどう汚れているかが全部わかってしまう。
#  まずは data/ の中身を自分の目で見て、汚れを自分で見つけるところから
#  始めることをおすすめする。
#
#  なお、これを読んでもFLAGは手に入らない。FLAGは check.py が起動時に
#  ランダム生成し、出力が仕様を満たしている間だけ書き出すため。
#  データも実行のたびに変わるので、答えを覚えることもできない。
# ============================================================================
import csv
import datetime
import os
import random
import secrets

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

DATA = "/data"
TRUTH = "/truth"

SURNAMES = ["佐藤", "鈴木", "高橋", "田中", "伊藤", "渡辺", "山本", "中村",
            "小林", "加藤", "吉田", "山田", "佐々木", "山口", "松本", "井上"]
GIVEN = ["太郎", "花子", "一郎", "美咲", "健太", "由紀", "翔", "彩",
         "大輔", "恵子", "拓也", "涼子", "直樹", "沙織", "隆", "真弓"]

REGIONS = ["east", "west", "north", "south"]
STATUSES = ["completed", "cancelled", "pending"]
NULLISH = ["NULL", "N/A", "-", ""]
UNIT_PRICES = [300, 480, 780, 980, 1200, 1980, 2480, 3200, 4800, 9800]

# 件数は実行ごとに振り直す。固定にすると正解の行数が毎回同じになり、
# 前回の答えや他人の答えが当てになってしまう
RANGE_ORDERS = (1050, 1400)
RANGE_DUPLICATED = (70, 110)    # 後から正しい値が届く注文
RANGE_SUPERSEDED = (10, 25)     # 後から届いた行が不正で、除外されるべき注文
RANGE_BROKEN = (25, 55)         # 1行しか無く、その行が不正な注文
RANGE_NULL_NAME = (10, 30)      # 顧客名が欠損表現になっている注文

RAW_COLUMNS = ["order_id", "order_date", "customer_name", "region",
               "status", "quantity", "amount", "ingested_at"]
# ファイルBだけ列の並びが違う。取り込みは列順に依存してはいけない
RAW_COLUMNS_B = ["ingested_at", "order_id", "customer_name", "order_date",
                 "region", "quantity", "amount", "status"]


def to_fullwidth_digits(s):
    return "".join(chr(ord(c) - ord("0") + ord("０")) if c.isdigit() else c for c in s)


def fmt_date(d, style):
    if style == "iso":
        return d.isoformat()
    if style == "slash":
        return f"{d.year}/{d.month:02d}/{d.day:02d}"
    if style == "jp":
        return f"{d.year}年{d.month}月{d.day}日"
    raise ValueError(style)


def fmt_amount(a, style, rng):
    if style == "plain":
        return str(a) if rng.random() > 0.15 else f"{a}.0"
    if style == "comma":
        return f"{a:,}"
    if style == "yen":
        return rng.choice([f"￥{a:,}", f"{a:,}円", f"￥{a}", str(a)])
    raise ValueError(style)


def fmt_quantity(q, style, rng):
    if style == "fullwidth" and rng.random() < 0.3:
        return to_fullwidth_digits(str(q))
    return str(q)


def fmt_case(value, style, rng):
    if style == "lower":
        return value if rng.random() > 0.2 else value.title()
    if style == "upper":
        return value.upper() if rng.random() < 0.4 else value
    if style == "title":
        return value.title()
    raise ValueError(style)


def fmt_name(name, style, rng):
    if style == "ideographic":
        return f"　{name}　"
    if rng.random() < 0.25:
        return f"  {name} "
    return name


STYLES = {
    # ファイルごとの表記の癖
    "A": dict(date="iso", amount="plain", qty="plain", case="lower", name="ascii"),
    "B": dict(date="slash", amount="comma", qty="fullwidth", case="upper", name="ascii"),
    "C": dict(date="jp", amount="yen", qty="plain", case="title", name="ideographic"),
}


def render_row(order, style_key, rng, override=None):
    """1件の注文を、指定されたファイルの表記ルールで1行のdictにする。"""
    s = STYLES[style_key]
    v = dict(order)
    if override:
        v.update(override)

    row = {
        "order_id": v["order_id"],
        "order_date": fmt_date(v["order_date"], s["date"]) if v["order_date"] else v["_date_raw"],
        "customer_name": (fmt_name(v["customer_name"], s["name"], rng)
                          if v["customer_name"] is not None else v["_name_raw"]),
        "region": fmt_case(v["region"], s["case"], rng),
        "status": fmt_case(v["status"], s["case"], rng),
        "quantity": (fmt_quantity(v["quantity"], s["qty"], rng)
                     if v["quantity"] is not None else v["_qty_raw"]),
        "amount": (fmt_amount(v["amount"], s["amount"], rng)
                   if v["amount"] is not None else v["_amount_raw"]),
        "ingested_at": v["ingested_at"].strftime("%Y-%m-%d %H:%M:%S"),
    }
    return row


def write_csv(path, rows, columns, encoding):
    with open(path, "w", encoding=encoding, newline="") as f:
        w = csv.DictWriter(f, fieldnames=columns)
        w.writeheader()
        for r in rows:
            w.writerow({c: r[c] for c in columns})


def main():
    os.makedirs(DATA, exist_ok=True)
    os.makedirs(TRUTH, exist_ok=True)

    rng = random.Random(secrets.randbits(64))
    base_ingest = datetime.datetime(2024, 2, 1, 2, 0, 0)

    n_orders = rng.randint(*RANGE_ORDERS)
    n_duplicated = rng.randint(*RANGE_DUPLICATED)
    n_superseded = rng.randint(*RANGE_SUPERSEDED)
    n_broken = rng.randint(*RANGE_BROKEN)
    n_null_name = rng.randint(*RANGE_NULL_NAME)

    orders = []
    for i in range(1, n_orders + 1):
        qty = rng.randint(1, 9)
        orders.append({
            "order_id": f"ORD-{i:06d}",
            "order_date": datetime.date(2024, 1, rng.randint(1, 31)),
            "customer_name": rng.choice(SURNAMES) + " " + rng.choice(GIVEN),
            "region": rng.choice(REGIONS),
            "status": rng.choice(STATUSES),
            "quantity": qty,
            "amount": qty * rng.choice(UNIT_PRICES),
            # ingested_at は全行で一意にしておく。最新行の判定を曖昧にしないため
            "ingested_at": base_ingest + datetime.timedelta(seconds=i),
        })

    idx = list(range(n_orders))
    rng.shuffle(idx)
    cut1 = n_duplicated
    cut2 = cut1 + n_superseded
    cut3 = cut2 + n_broken
    cut4 = cut3 + n_null_name
    duplicated = set(idx[:cut1])
    superseded = set(idx[cut1:cut2])
    broken = set(idx[cut2:cut3])
    null_name = set(idx[cut3:cut4])

    for i in null_name:
        orders[i]["customer_name"] = None
        orders[i]["_name_raw"] = rng.choice(NULLISH)

    def bucket(d):
        if d.day <= 10:
            return "A"
        if d.day <= 20:
            return "B"
        return "C"

    files = {"A": [], "B": [], "C": []}
    late = []
    late_base = datetime.datetime(2024, 2, 2, 3, 0, 0)

    def broken_override(rng, when):
        """除外されるべき行にするための差し替え。"""
        kind = rng.choice(["qty_missing", "qty_zero", "qty_negative",
                           "amount_missing", "date_missing"])
        o = {"ingested_at": when}
        if kind == "qty_missing":
            o.update(quantity=None, _qty_raw=rng.choice(NULLISH))
        elif kind == "qty_zero":
            o.update(quantity=0)
        elif kind == "qty_negative":
            o.update(quantity=-rng.randint(1, 3))
        elif kind == "amount_missing":
            o.update(amount=None, _amount_raw=rng.choice(NULLISH))
        elif kind == "date_missing":
            o.update(order_date=None, _date_raw=rng.choice(NULLISH))
        return o

    for i, order in enumerate(orders):
        b = bucket(order["order_date"])

        if i in duplicated:
            # 先に届いた行は古い値。正しい値は後から late ファイルで届く
            stale_qty = max(1, order["quantity"] + rng.choice([-2, -1, 1, 2]))
            stale = {
                "status": rng.choice([s for s in STATUSES if s != order["status"]]),
                "quantity": stale_qty,
                "amount": stale_qty * rng.choice(UNIT_PRICES),
                "ingested_at": order["ingested_at"] - datetime.timedelta(hours=6),
            }
            files[b].append(render_row(order, b, rng, stale))
            late.append(render_row(order, "A", rng,
                                   {"ingested_at": late_base + datetime.timedelta(seconds=i)}))

        elif i in superseded:
            # 先に届いた行は正常。後から届いた行が不正なので、この注文は落ちる
            files[b].append(render_row(order, b, rng,
                                       {"ingested_at": order["ingested_at"]
                                        - datetime.timedelta(hours=6)}))
            late.append(render_row(order, "A", rng,
                                   broken_override(rng, late_base
                                                   + datetime.timedelta(seconds=i))))

        elif i in broken:
            files[b].append(render_row(order, b, rng,
                                       broken_override(rng, order["ingested_at"])))

        else:
            files[b].append(render_row(order, b, rng))

    for rows in files.values():
        rng.shuffle(rows)
    rng.shuffle(late)

    write_csv(f"{DATA}/orders_2024-01-01_2024-01-10.csv", files["A"], RAW_COLUMNS, "utf-8")
    write_csv(f"{DATA}/orders_2024-01-11_2024-01-20.csv", files["B"], RAW_COLUMNS_B, "utf-8")
    write_csv(f"{DATA}/orders_2024-01-21_2024-01-31.csv", files["C"], RAW_COLUMNS, "cp932")
    write_csv(f"{DATA}/orders_late_2024-02-02.csv", late, RAW_COLUMNS, "utf-8")

    dropped = superseded | broken
    expected = [o for i, o in enumerate(orders) if i not in dropped]
    expected.sort(key=lambda o: o["order_id"])

    df = pd.DataFrame({
        "order_id": [o["order_id"] for o in expected],
        "order_date": [o["order_date"] for o in expected],
        "customer_name": [o["customer_name"] for o in expected],
        "region": [o["region"] for o in expected],
        "status": [o["status"] for o in expected],
        "quantity": [o["quantity"] for o in expected],
        "amount_jpy": [o["amount"] for o in expected],
    })
    schema = pa.schema([
        ("order_id", pa.string()),
        ("order_date", pa.date32()),
        ("customer_name", pa.string()),
        ("region", pa.string()),
        ("status", pa.string()),
        ("quantity", pa.int32()),
        ("amount_jpy", pa.int64()),
    ])
    pq.write_table(pa.Table.from_pandas(df, schema=schema, preserve_index=False),
                   f"{TRUTH}/expected.parquet")

    print(f"[gen] 生データを {DATA} に生成しました "
          f"(注文 {n_orders} 件 / 正解 {len(expected)} 行)")


if __name__ == "__main__":
    main()
