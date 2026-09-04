"""今出ている3問の参考解答を出す。

questions.py には全問の解答が入っているが、そちらを開くとこれから出る問の
答えまで見えてしまう。ここは work/.quest.json に載っている3問だけを出す。
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import questions

STATE = Path(__file__).resolve().parent / "work" / ".quest.json"


def main() -> int:
    if not STATE.exists():
        print("問題がまだ配られていない。mk quest-02-new を叩くこと")
        return 1

    state = json.loads(STATE.read_text(encoding="utf-8"))
    print(f"\nseed={state['seed']} の参考解答\n")
    for i, qid in enumerate(state["ids"], start=1):
        q = questions.BY_ID[qid]
        print(f"# 問{i} [{q.section}] {q.ask}")
        print(f"ans{i} = {q.answer}\n")

    print("同じ結果になる書き方なら何でも正解になる。判定は値を見ている")
    return 0


if __name__ == "__main__":
    sys.exit(main())
