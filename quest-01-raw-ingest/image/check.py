#!/usr/bin/env python3
# 出力を10秒ごとに検証し、仕様を満たしている間だけFLAGを置く見張り役。
#
# FLAGはこのプロセスが起動した瞬間にランダム生成され、メモリ上にしか無い。
# どのファイルにも平文で書かれていないし、コンテナを立て直せば変わる。
import datetime
import os
import secrets
import time
import traceback

import pyarrow as pa
import pyarrow.parquet as pq

OUT_PARQUET = "/out/orders.parquet"
OUT_FLAG = "/out/flag.txt"
OUT_REPORT = "/out/report.txt"
TRUTH = "/truth/expected.parquet"

INTERVAL = 10
MAX_EXAMPLES = 3

SPEC = [
    ("order_id", pa.string()),
    ("order_date", pa.date32()),
    ("customer_name", pa.string()),
    ("region", pa.string()),
    ("status", pa.string()),
    ("quantity", pa.int32()),
    ("amount_jpy", pa.int64()),
]
SPEC_NAMES = [n for n, _ in SPEC]

FLAG = "FLAG{" + secrets.token_hex(16) + "}"


class Failure(Exception):
    """このチェックで打ち切る、という意味の失敗。以降のチェックは実行しない。"""


def load_expected():
    t = pq.read_table(TRUTH)
    return {name: t.column(name).to_pylist() for name in SPEC_NAMES}, t.num_rows


def check_schema(table, lines):
    got = table.schema.names
    if got != SPEC_NAMES:
        missing = [c for c in SPEC_NAMES if c not in got]
        extra = [c for c in got if c not in SPEC_NAMES]
        detail = []
        if missing:
            detail.append(f"足りない列: {missing}")
        if extra:
            detail.append(f"余計な列: {extra}")
        if not detail:
            detail.append(f"列の並びが違う: {got}")
        raise Failure("列 … NG  " + " / ".join(detail))
    lines.append("列 … OK")

    bad = [f"{n}: 期待 {t} / 実際 {table.schema.field(n).type}"
           for n, t in SPEC if table.schema.field(n).type != t]
    if bad:
        raise Failure("型 … NG  " + " / ".join(bad))
    lines.append("型 … OK")


def check_keys(actual, expected, n_expected, lines):
    ids = actual["order_id"]
    if len(ids) != len(set(ids)):
        dup = sorted({i for i in ids if ids.count(i) > 1})[:MAX_EXAMPLES]
        raise Failure(f"order_idの一意性 … NG  重複している: {dup} ...")
    lines.append("order_idの一意性 … OK")

    if ids != sorted(ids):
        raise Failure("並び順 … NG  order_id の昇順になっていない")
    lines.append("並び順 … OK")

    got, want = set(ids), set(expected["order_id"])
    if got != want:
        extra = sorted(got - want)[:MAX_EXAMPLES]
        missing = sorted(want - got)[:MAX_EXAMPLES]
        detail = [f"行数 期待 {n_expected} / 実際 {len(ids)}"]
        if extra:
            detail.append(f"あってはいけない order_id: {extra} ...({len(got - want)}件)")
        if missing:
            detail.append(f"足りない order_id: {missing} ...({len(want - got)}件)")
        raise Failure("行の集合 … NG  " + " / ".join(detail))
    lines.append(f"行の集合 … OK ({n_expected} 行)")


def check_values(actual, expected, lines):
    ok = True
    pos = {oid: i for i, oid in enumerate(expected["order_id"])}
    order = [pos[oid] for oid in actual["order_id"]]

    for col in SPEC_NAMES[1:]:
        got = actual[col]
        want = [expected[col][i] for i in order]
        diffs = [(actual["order_id"][i], got[i], want[i])
                 for i in range(len(got)) if got[i] != want[i]]
        if not diffs:
            lines.append(f"{col} … OK")
            continue
        ok = False
        lines.append(f"{col} … NG  {len(diffs)} 行が不一致")
        for oid, g, w in diffs[:MAX_EXAMPLES]:
            lines.append(f"    {oid}  実際: {g!r}  期待: {w!r}")
    if not ok:
        raise Failure(None)


def run_checks():
    """(合格したか, レポートの本文) を返す。"""
    lines = []
    if not os.path.exists(OUT_PARQUET):
        return False, [f"{OUT_PARQUET} がまだありません。./run.sh で ingest.py を実行してください。"]

    try:
        table = pq.read_table(OUT_PARQUET)
    except Exception as e:
        return False, [f"Parquetとして読めません … NG  {type(e).__name__}: {e}"]

    expected, n_expected = load_expected()
    try:
        check_schema(table, lines)
        actual = {name: table.column(name).to_pylist() for name in SPEC_NAMES}
        check_keys(actual, expected, n_expected, lines)
        check_values(actual, expected, lines)
    except Failure as e:
        if e.args and e.args[0]:
            lines.append(str(e))
        return False, lines
    return True, lines


def write_report(passed, lines):
    stamp = datetime.datetime.now().strftime("%H:%M:%S")
    head = f"=== {stamp}  {'すべて合格' if passed else '未達'} ==="
    body = "\n".join([head] + lines) + "\n"
    if passed:
        body += "\nFLAGが out/flag.txt に置かれました。\n"
    tmp = OUT_REPORT + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(body)
    os.replace(tmp, OUT_REPORT)


def main():
    print("[check] 10秒ごとに /out/orders.parquet を検証します", flush=True)
    while True:
        try:
            passed, lines = run_checks()
        except Exception:
            passed, lines = False, ["検証中に想定外のエラー:", traceback.format_exc()]

        if passed:
            tmp = OUT_FLAG + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                f.write(FLAG + "\n")
            os.replace(tmp, OUT_FLAG)
        elif os.path.exists(OUT_FLAG):
            os.remove(OUT_FLAG)

        write_report(passed, lines)
        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
