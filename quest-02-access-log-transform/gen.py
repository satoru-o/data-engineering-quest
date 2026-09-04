"""quest-02 の出題。seed を決め、3問を引き、データと work/solve.py を作る。

引き直しは gen.py を呼んだときだけ起きる。mk quest-02 は
work/.quest.json があれば gen.py を呼ばないので、解いている最中に
問題が変わることはない (変わったら直しようがない)。

    SEED=1234 python gen.py     同じ問題を再現する
"""

from __future__ import annotations

import json
import os
import random
import sys
from pathlib import Path

import questions

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
WORK = ROOT / "work"
LOG_CSV = DATA / "access_log.csv"
SCREENS_CSV = DATA / "screens.csv"
SOLVE = WORK / "solve.py"
STATE = WORK / ".quest.json"

HEADER = '''"""quest-02: アクセスログの下ごしらえ。

書き換えるのは ansN = ... の右辺だけ。1問1行で書ける。
書き方は ../../CHEATSHEET.md の [ ] に出ている節に載っている。

    mk quest-02          採点する
    mk quest-02-answer   今の3問の参考解答を見る
    mk quest-02-new      別の3問を引き直す (この答えは消える)
"""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "access_log.csv"
{screens_path}
df = pd.read_csv(SRC)
{screens_read}
# 届いたそのままの姿。全部が文字列で入っている
print(df.head())
'''


def render_solve(picked: list[questions.Question], with_screens: bool) -> str:
    """選ばれた問から work/solve.py を組み立てる。"""
    screens_path = 'SCREENS = ROOT / "data" / "screens.csv"\n' if with_screens else ""
    screens_read = "screens = pd.read_csv(SCREENS)\n" if with_screens else ""
    parts = [HEADER.format(screens_path=screens_path, screens_read=screens_read)]

    for i, q in enumerate(picked, start=1):
        parts.append(
            f"\n# 問{i} [{q.section}] {q.ask}\n"
            f"ans{i} = ...  # ← この右辺を書き換える\n"
        )
    return "".join(parts)


def main() -> int:
    raw_seed = os.environ.get("SEED", "").strip()
    if raw_seed:
        try:
            seed = int(raw_seed)
        except ValueError:
            print(f"SEED は整数で指定すること (指定された値: {raw_seed!r})")
            return 1
    else:
        seed = random.randrange(1000, 10000)

    rng = random.Random(seed)
    picked = questions.pick(rng)

    needs: set[str] = set()
    for q in picked:
        needs |= q.needs

    DATA.mkdir(exist_ok=True)
    WORK.mkdir(exist_ok=True)

    log = questions.make_log(rng, needs)
    log.to_csv(LOG_CSV, index=False)

    with_screens = "screens" in needs
    SCREENS_CSV.unlink(missing_ok=True)
    if with_screens:
        questions.make_screens(log).to_csv(SCREENS_CSV, index=False)

    SOLVE.write_text(render_solve(picked, with_screens), encoding="utf-8")
    STATE.write_text(
        json.dumps({"seed": seed, "ids": [q.id for q in picked]}, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"新しい問題を配った (seed={seed})")
    for i, q in enumerate(picked, start=1):
        print(f"  問{i} [{q.section}] {q.ask}")
    print(f"\n{SOLVE} を開いて ansN の右辺を書く")
    return 0


if __name__ == "__main__":
    sys.exit(main())
