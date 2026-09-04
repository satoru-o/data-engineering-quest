"""quest-02 の出題バンクとデータ生成。gen.py と check.py の両方が読む。

> [!WARNING]
> このファイルには全問の参考解答が入っている。開くと答えが見えてしまう。
> 答えが見たいだけなら `mk quest-02-answer` を叩くこと。今出ている3問だけを出す。

期待値は各問の solve (pandas の参照実装) をその場で評価して作っている。
groupby や merge の期待値を素の Python で書き直すこともできるが、
分量が増えるうえに参照実装と二重管理になり、間違えたときに
「問題が壊れているのか自分が間違えているのか」が分からなくなる。

問題は CHEATSHEET.md の節に対応している。section の文字列は
チートシートの見出しとそのまま同じにしてあり、採点結果にもこれを出す。
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Callable

import pandas as pd

# CHEATSHEET.md の節のうち、自動採点できるもの。出題はこの9つから引く。
# 「まず形を見る」は見るだけで変換しない、「読む / 書く」は問題の外側、
# 「よくある落とし穴」は独立した操作ではないので、いずれも出題しない
SECTIONS = [
    "型を直す",
    "文字列",
    "欠損",
    "重複",
    "行を選ぶ",
    "列を作る・直す",
    "日時",
    "集約",
    "結合",
]

# 1回に出す問数。違う節から引くので SECTIONS の数を超えられない
N_QUESTIONS = 3


@dataclass(frozen=True)
class Question:
    """1問。

    id      安定した識別子。work/.quest.json に保存して次回の採点で引き当てる
    section CHEATSHEET.md の節名。採点結果に [ ] で出る
    ask     問題文。solve.py にコメントとして埋まる
    answer  参考解答。mk quest-02-answer が出す
    solve   参照実装。これを評価したものが期待値になる
    needs   データ生成への要求。この問が引かれたときだけ汚れを載せる
    """

    id: str
    section: str
    ask: str
    answer: str
    solve: Callable[[pd.DataFrame], object]
    needs: set[str] = field(default_factory=set)


# --------------------------------------------------------------------------
# 出題バンク
#
# 各節から2問ずつ。同じ節の2問は「よく使うほう」と「もう一段いるほう」に
# なるようにしてある (例: 欠損なら fillna と dropna(subset=))
# --------------------------------------------------------------------------

BANK: list[Question] = [
    # ---- 型を直す --------------------------------------------------------
    Question(
        id="type-ts",
        section="型を直す",
        ask="ts を datetime64[ns, UTC] にした Series (末尾の Z と +09:00 が混ざっている)",
        answer='pd.to_datetime(df["ts"], utc=True)',
        solve=lambda df: pd.to_datetime(df["ts"], utc=True),
        needs={"mixed_tz"},
    ),
    Question(
        id="type-status",
        section="型を直す",
        ask='status を Int64 にした Series ("-" は欠損として扱う)',
        answer='pd.to_numeric(df["status"], errors="coerce").astype("Int64")',
        solve=lambda df: pd.to_numeric(df["status"], errors="coerce").astype("Int64"),
        needs={"status_missing"},
    ),
    # ---- 文字列 ----------------------------------------------------------
    Question(
        id="str-dur",
        section="文字列",
        ask='dur を「秒の float64」にした Series ("1.2s" -> 1.2)',
        answer='df["dur"].str.removesuffix("s").astype("float64")',
        solve=lambda df: df["dur"].str.removesuffix("s").astype("float64"),
    ),
    Question(
        id="str-bytes",
        section="文字列",
        ask='bytes を int64 にした Series (桁区切りのカンマを落とす。"1,234" -> 1234)',
        answer='df["bytes"].str.replace(",", "", regex=False).astype("int64")',
        solve=lambda df: df["bytes"].str.replace(",", "", regex=False).astype("int64"),
    ),
    # ---- 欠損 ------------------------------------------------------------
    Question(
        id="na-fill",
        section="欠損",
        ask='user_id の欠損を "anonymous" で埋めた Series',
        answer='df["user_id"].fillna("anonymous")',
        solve=lambda df: df["user_id"].fillna("anonymous"),
        needs={"user_missing"},
    ),
    Question(
        id="na-drop",
        section="欠損",
        ask="user_id が欠損している行を落とした DataFrame (他の列の欠損では落とさない)",
        answer='df.dropna(subset=["user_id"])',
        solve=lambda df: df.dropna(subset=["user_id"]),
        needs={"user_missing"},
    ),
    # ---- 重複 ------------------------------------------------------------
    Question(
        id="dup-all",
        section="重複",
        ask="完全に同じ行の重複を落とした DataFrame (最初に来たほうを残す)",
        answer="df.drop_duplicates()",
        solve=lambda df: df.drop_duplicates(),
        needs={"dup_rows"},
    ),
    Question(
        id="dup-subset",
        section="重複",
        ask="同じ (ts, path) の重複を落とした DataFrame。後から来たほうを残す",
        answer='df.drop_duplicates(subset=["ts", "path"], keep="last")',
        solve=lambda df: df.drop_duplicates(subset=["ts", "path"], keep="last"),
        needs={"dup_rows"},
    ),
    # ---- 行を選ぶ --------------------------------------------------------
    Question(
        id="filter-5xx",
        section="行を選ぶ",
        ask="status が 500 以上の行だけの DataFrame (status は文字列のままなので先に数値にする)",
        answer='df[pd.to_numeric(df["status"], errors="coerce") >= 500]',
        solve=lambda df: df[pd.to_numeric(df["status"], errors="coerce") >= 500],
        needs={"status_missing", "server_errors"},
    ),
    Question(
        id="filter-api",
        section="行を選ぶ",
        ask='path が "/api" で始まる行だけの DataFrame',
        answer='df[df["path"].str.startswith("/api")]',
        solve=lambda df: df[df["path"].str.startswith("/api")],
        needs={"api_paths"},
    ),
    # ---- 列を作る・直す --------------------------------------------------
    Question(
        id="col-add",
        section="列を作る・直す",
        ask='dur を秒の float64 にした列 dur_sec を足した DataFrame (元の dur は残す)',
        answer='df.assign(dur_sec=df["dur"].str.removesuffix("s").astype("float64"))',
        solve=lambda df: df.assign(
            dur_sec=df["dur"].str.removesuffix("s").astype("float64")
        ),
    ),
    Question(
        id="col-rename",
        section="列を作る・直す",
        ask="列 ts を requested_at に、dur を duration に改名した DataFrame",
        answer='df.rename(columns={"ts": "requested_at", "dur": "duration"})',
        solve=lambda df: df.rename(columns={"ts": "requested_at", "dur": "duration"}),
    ),
    # ---- 日時 ------------------------------------------------------------
    Question(
        id="dt-hour",
        section="日時",
        ask="ts の「UTCでの時」だけを取り出した int32 の Series (先に datetime にする)",
        answer='pd.to_datetime(df["ts"], utc=True).dt.hour',
        solve=lambda df: pd.to_datetime(df["ts"], utc=True).dt.hour,
        needs={"mixed_tz"},
    ),
    Question(
        id="dt-jst",
        section="日時",
        ask="ts を日本時間に直した Series (datetime64[ns, Asia/Tokyo])",
        answer='pd.to_datetime(df["ts"], utc=True).dt.tz_convert("Asia/Tokyo")',
        solve=lambda df: pd.to_datetime(df["ts"], utc=True).dt.tz_convert("Asia/Tokyo"),
        needs={"mixed_tz"},
    ),
    # ---- 集約 ------------------------------------------------------------
    Question(
        id="agg-count",
        section="集約",
        ask="path ごとの件数の Series (添字が path、値が件数)",
        answer='df.groupby("path").size()',
        solve=lambda df: df.groupby("path").size(),
    ),
    Question(
        id="agg-named",
        section="集約",
        ask=(
            "path ごとに 件数 と 平均秒 を出した DataFrame。"
            "列名は path / 件数 / 平均秒 の3つ (path は添字ではなく列)"
        ),
        answer=(
            'df.assign(秒=df["dur"].str.removesuffix("s").astype("float64"))'
            '.groupby("path").agg(件数=("秒", "size"), 平均秒=("秒", "mean")).reset_index()'
        ),
        solve=lambda df: df.assign(
            秒=df["dur"].str.removesuffix("s").astype("float64")
        )
        .groupby("path")
        .agg(件数=("秒", "size"), 平均秒=("秒", "mean"))
        .reset_index(),
    ),
    # ---- 結合 ------------------------------------------------------------
    Question(
        id="join-left",
        section="結合",
        ask=(
            "data/screens.csv を path で左結合し、画面名の列を足した DataFrame。"
            "左の行はすべて残す (screens = pd.read_csv(SCREENS) で読んである)"
        ),
        answer='df.merge(screens, on="path", how="left")',
        solve=lambda df: df.merge(_screens(df), on="path", how="left"),
        needs={"screens"},
    ),
    Question(
        id="join-inner",
        section="結合",
        ask=(
            "data/screens.csv に載っている path の行だけを、画面名付きで残した DataFrame。"
            "(screens = pd.read_csv(SCREENS) で読んである)"
        ),
        answer='df.merge(screens, on="path", how="inner")',
        solve=lambda df: df.merge(_screens(df), on="path", how="inner"),
        needs={"screens"},
    ),
]


# 結合の問だけ、参照実装がマスタ側を要る。gen.py が作った CSV を読んで渡す。
# df に属性として貼っておく (lambda の引数を1つに揃えたいので)
def _screens(df: pd.DataFrame) -> pd.DataFrame:
    return df.attrs["screens"]


BY_ID = {q.id: q for q in BANK}


def pick(rng: random.Random, n: int = N_QUESTIONS) -> list[Question]:
    """違う節から n 問引く。節を先に選んでから、その節の中で1問選ぶ。

    バンクから直接 n 問引くと、問数の多い節ばかり当たる。
    節を等確率にしたいので二段階で引いている
    """
    sections = rng.sample(SECTIONS, n)
    out = []
    for s in sections:
        out.append(rng.choice([q for q in BANK if q.section == s]))
    return out


# --------------------------------------------------------------------------
# データ生成
# --------------------------------------------------------------------------

PATHS = ["/", "/items", "/cart", "/checkout", "/login", "/health", "/items/1001"]
API_PATHS = ["/api/search", "/api/cart", "/api/items"]
SCREEN_NAMES = {
    "/": "トップ",
    "/items": "商品一覧",
    "/cart": "カート",
    "/checkout": "レジ",
    "/login": "ログイン",
    "/api/search": "検索API",
    "/api/cart": "カートAPI",
}


JST = timezone(timedelta(hours=9))


def iso(at: datetime, rng: random.Random, mixed: bool) -> str:
    """時刻を ISO8601 の文字列にする。

    mixed のときは、同じ瞬間を UTC ("...Z") と 日本時間 ("...+09:00") の
    どちらかで書く。実際のログでも、送信元のサーバによって時間帯の書き方が
    揃わないことがある。

    表記を揃えてしまうと pd.to_datetime(s) が utc=True 無しでも
    datetime64[ns, UTC] を返してしまい、「型を直す」の問が成立しない。
    混ざっていて初めて utc=True が要る (無いと object になり警告が出る)
    """
    if mixed and rng.random() < 0.4:
        return at.astimezone(JST).strftime("%Y-%m-%dT%H:%M:%S+09:00")
    return at.strftime("%Y-%m-%dT%H:%M:%SZ")


def make_log(rng: random.Random, needs: set[str]) -> pd.DataFrame:
    """アクセスログを作る。needs に入っている汚れだけを載せる。

    引かれなかった問のための汚れまで載せると、問題に関係のないところで
    引っかかって時間を取られる。出題を先に決めてからデータを作っているのはそのため
    """
    n = rng.randint(15, 30)
    paths = list(PATHS)
    if "api_paths" in needs:
        paths += API_PATHS

    # 開始時刻をずらして、毎回違う時間帯のログにする
    at = datetime(2026, 1, 5, rng.randint(0, 21), rng.randint(0, 30), tzinfo=timezone.utc)

    rows = []
    for _ in range(n):
        at += timedelta(seconds=rng.randint(20, 240))
        rows.append(
            {
                "_at": at,  # 並べ替え用。CSV には出さない
                "ts": iso(at, rng, "mixed_tz" in needs),
                "path": rng.choice(paths),
                "status": str(rng.choice([200, 200, 200, 301, 404])),
                "dur": f"{rng.randint(1, 900) / 100:.2f}s",
                "bytes": f"{rng.randint(200, 900_000):,}",
                "user_id": f"u{rng.randint(1, 40):03d}",
            }
        )

    if "server_errors" in needs:
        # 500以上が1件も無いと「行を選ぶ」の答えが空になり、解けたのか
        # 間違えたのか分からなくなる。必ず何件か混ぜる
        for i in rng.sample(range(len(rows)), k=rng.randint(2, 4)):
            rows[i]["status"] = str(rng.choice([500, 502, 503]))

    if "status_missing" in needs:
        for i in rng.sample(range(len(rows)), k=rng.randint(2, 4)):
            rows[i]["status"] = "-"

    if "user_missing" in needs:
        for i in rng.sample(range(len(rows)), k=rng.randint(2, 5)):
            rows[i]["user_id"] = ""

    if "dup_rows" in needs:
        # 丸ごと同じ行と、(ts, path) だけ同じで中身が違う行の両方を入れる。
        # drop_duplicates() と drop_duplicates(subset=) で答えが変わるようにするため
        for i in rng.sample(range(len(rows)), k=rng.randint(1, 3)):
            rows.append(dict(rows[i]))
        for i in rng.sample(range(len(rows)), k=rng.randint(1, 2)):
            near = dict(rows[i])
            near["dur"] = f"{rng.randint(1, 900) / 100:.2f}s"
            rows.append(near)
        rng.shuffle(rows)

    # ログなので時刻順に並べる。ts の文字列で並べると +09:00 の行が
    # 見かけの時刻で混ざるので、生成時に持っておいた瞬間で並べる。
    # 重複を足したあとに並べるため、同じ (ts, path) の行は隣り合う
    rows.sort(key=lambda r: r["_at"])
    return pd.DataFrame(rows).drop(columns=["_at"])


def make_screens(log: pd.DataFrame) -> pd.DataFrame:
    """path -> 画面名 のマスタ。

    わざと全部の path を載せていない。左結合なら画面名が欠損の行が残り、
    内部結合なら行が減る。how= の違いが結果に出るようにするため
    """
    known = [p for p in log["path"].unique() if p in SCREEN_NAMES]
    known.sort()
    return pd.DataFrame({"path": known, "画面名": [SCREEN_NAMES[p] for p in known]})
