# pandas チートシート

**これは見ながら書くためのものです。** 覚えてから書くのではなく、引いて書いて、
あとから覚えます。クエスト中に開いたままにしておいて構いません。

思い出そうとして手が止まったら、それは覚えていないのではなく、
まだ引く回数が足りていないだけです。

`df` は DataFrame、`s` は Series を指します。
`pd` は `import pandas as pd`、`np` は `import numpy as np` の略です。

---

## まず形を見る

書き始める前にこれを見ます。**どこが汚れているかを見てから直すほうが速いです。**

| | |
|---|---|
| 行数と列数 | `df.shape` |
| 列ごとの型 | `df.dtypes` |
| 先頭を見る | `df.head()` / 末尾は `df.tail()` |
| 型と欠損をまとめて | `df.info()` |
| 数値の分布 | `df.describe()` |
| その列に何が入っているか | `df["x"].value_counts(dropna=False)` |
| 列ごとの欠損の数 | `df.isna().sum()` |
| 重複行の数 | `df.duplicated().sum()` |

> [!TIP]
> `value_counts(dropna=False)` は表記ゆれ探しの定番です。
> `"東京"` と `"東京都"` が別物として並ぶので、一目で分かります。

## 読む / 書く

| | |
|---|---|
| CSV を読む | `df = pd.read_csv("x.csv")` |
| 文字コードを指定 | `pd.read_csv("x.csv", encoding="cp932")` |
| 読みながら型を指定 | `pd.read_csv("x.csv", dtype={"id": "string"})` |
| 読みながら日付にする | `pd.read_csv("x.csv", parse_dates=["ts"])` |
| この文字列を欠損とみなす | `pd.read_csv("x.csv", na_values=["-", "N/A", "不明"])` |
| 区切りがタブ | `pd.read_csv("x.tsv", sep="\t")` |
| ヘッダが無い | `pd.read_csv("x.csv", header=None, names=["a", "b"])` |
| JSON を読む | `pd.read_json("x.json")` / 1行1JSONは `lines=True` |
| Parquet を読む | `pd.read_parquet("x.parquet")` |
| CSV に書く | `df.to_csv("x.csv", index=False)` |
| Parquet に書く | `df.to_parquet("x.parquet", index=False)` |

> [!IMPORTANT]
> **CSV に書くと型が消えます。** 読み直すとまた全部が文字列や推測された型になります。
> 型を保ったまま次の工程に渡したいときは Parquet を使います。

## 型を直す

ETL でいちばん時間を使うところです。

| | |
|---|---|
| 文字列を日時に | `pd.to_datetime(s)` |
| 末尾が `Z` (UTC) の日時 | `pd.to_datetime(s, utc=True)` → `datetime64[ns, UTC]` |
| 書式を明示する | `pd.to_datetime(s, format="%Y/%m/%d")` |
| 書式が混ざっている | `pd.to_datetime(s, format="mixed")` |
| 変換できない値を欠損に | `pd.to_datetime(s, errors="coerce")` |
| 文字列を数値に | `pd.to_numeric(s)` |
| 数値にできない値を欠損に | `pd.to_numeric(s, errors="coerce")` |
| 欠損を持てる整数にする | `s.astype("Int64")` |
| 小数にする | `s.astype("float64")` |
| 文字列型にする | `s.astype("string")` |
| 種類の少ない文字列を軽くする | `s.astype("category")` |
| 真偽値に写す | `s.map({"はい": True, "いいえ": False})` |

**よく使う組み合わせ:**

```python
# "200" と "-" が混ざった列を、欠損を持てる整数にする
df["status"] = pd.to_numeric(df["status"], errors="coerce").astype("Int64")
```

> [!IMPORTANT]
> `int64` と `Int64` は別物です。**頭が大文字のほうだけが欠損 (`<NA>`) を持てます。**
> 欠損のある列に `astype("int64")` を掛けると落ちます。

## 文字列

すべて `.str` を挟みます。挟み忘れが最も多い間違いです。

| | |
|---|---|
| 前後の空白を落とす | `s.str.strip()` |
| 置き換える | `s.str.replace(",", "", regex=False)` |
| 末尾を落とす | `s.str.removesuffix("s")` / 先頭は `removeprefix` |
| 端の文字を削る | `s.str.rstrip("s")` / `s.str.lstrip("#")` |
| 切り出す | `s.str[:-1]` / `s.str[0:3]` |
| 大文字・小文字 | `s.str.lower()` / `s.str.upper()` |
| 全角を半角に | `s.str.normalize("NFKC")` |
| 含むか | `s.str.contains("エラー", na=False)` |
| 前方一致 | `s.str.startswith("/api")` |
| 区切って列にする | `s.str.split("-", expand=True)` |
| 正規表現で取り出す | `s.str.extract(r"(\d+)")` |
| 長さ | `s.str.len()` |

**よく使う組み合わせ:**

```python
# "1,200円" -> 1200
df["amount"] = df["amount"].str.replace(",", "").str.replace("円", "").astype("int64")

# "1.2s" -> 1.2
df["dur"] = df["dur"].str.removesuffix("s").astype("float64")
```

## 欠損

| | |
|---|---|
| 欠損かどうか | `s.isna()` / 逆は `s.notna()` |
| 列ごとの数 | `df.isna().sum()` |
| 値で埋める | `s.fillna(0)` |
| 直前の値で埋める | `s.ffill()` / 直後は `s.bfill()` |
| 欠損のある行を落とす | `df.dropna()` |
| この列が欠損の行だけ落とす | `df.dropna(subset=["id"])` |
| 特定の値を欠損とみなす | `s.replace("-", pd.NA)` |

> [!WARNING]
> `df.dropna()` は**どこか1列でも欠損があれば行ごと落とします。**
> たいていは `subset=` で落とす基準の列を明示したほうが安全です。

## 重複

| | |
|---|---|
| 重複行を消す | `df.drop_duplicates()` |
| この列が同じなら重複とみなす | `df.drop_duplicates(subset=["order_id"])` |
| 最後の行を残す | `df.drop_duplicates(subset=["id"], keep="last")` |
| 重複を消さずに印だけ付ける | `df.duplicated(subset=["id"], keep=False)` |
| 重複している行を見る | `df[df.duplicated(subset=["id"], keep=False)]` |

> [!TIP]
> 訂正データを扱うときは `keep="last"` が効きます。
> ただし**先に時刻で並べておかないと「最後」が何を指すか決まりません**
> (`df.sort_values("updated_at")`)。

## 行を選ぶ

| | |
|---|---|
| 条件で絞る | `df[df["status"] >= 500]` |
| 条件を書きやすく | `df.query("status >= 500 and dur > 1.0")` |
| 複数条件 | `df[(df["a"] > 1) & (df["b"] < 2)]` — `and` ではなく `&`、括弧が要る |
| どれかに一致 | `df[df["path"].isin(["/cart", "/checkout"])]` |
| 範囲 | `df[df["dur"].between(1.0, 5.0)]` |
| 否定 | `df[~df["path"].str.startswith("/api")]` |
| 行と列を同時に | `df.loc[df["a"] > 1, ["a", "b"]]` |
| 位置で | `df.iloc[0:5]` |
| 上位 n 件 | `df.nlargest(5, "dur")` / 下位は `nsmallest` |

## 列を作る・直す

| | |
|---|---|
| 列を足す | `df["b"] = df["a"] * 2` |
| 元を壊さずに足す | `df = df.assign(b=df["a"] * 2)` |
| 名前を変える | `df.rename(columns={"旧": "新"})` |
| 列を落とす | `df.drop(columns=["tmp"])` |
| 列を並べ替える | `df = df[["id", "ts", "amount"]]` |
| 条件で値を分ける | `df["区分"] = np.where(df["a"] > 0, "正", "負")` |
| 条件が3つ以上 | `pd.cut(df["a"], bins=[0, 10, 100], labels=["小", "大"])` |
| 並べ替える | `df.sort_values(["ts", "id"])` |
| 添字を振り直す | `df.reset_index(drop=True)` |

## 日時

`datetime64` の列にだけ使えます。`.dt` を挟みます。

| | |
|---|---|
| 日付だけ | `s.dt.date` |
| 年 / 月 / 日 | `s.dt.year` / `s.dt.month` / `s.dt.day` |
| 時 | `s.dt.hour` |
| 曜日 | `s.dt.dayofweek` (月=0) / 名前は `s.dt.day_name()` |
| 時間帯を変える | `s.dt.tz_convert("Asia/Tokyo")` |
| 時間帯を付ける | `s.dt.tz_localize("Asia/Tokyo")` |
| 時間帯を外す | `s.dt.tz_localize(None)` |
| 1時間単位に丸める | `s.dt.floor("1h")` |
| 月初に寄せる | `s.dt.to_period("M")` — 時間帯が付いていると捨てられて警告が出ます |
| 差を取る | `df["終"] - df["始"]` → `timedelta64` |
| 差を秒にする | `(df["終"] - df["始"]).dt.total_seconds()` |
| 時間で集計する | `df.set_index("ts").resample("1h").size()` |

> [!WARNING]
> **時間帯の付いた日時 (tz-aware) と付いていない日時 (tz-naive) は比較できません。**
> どちらかに揃えてから比べます。`tz_convert` は既に付いているものを変換し、
> `tz_localize` は付いていないものに付けます。

## 集約

| | |
|---|---|
| 件数 | `df.groupby("path").size()` |
| 合計 | `df.groupby("path")["amount"].sum()` |
| 複数の集計を一度に | `df.groupby("path")["dur"].agg(["count", "mean", "max"])` |
| 列に名前を付けて集計 | 下の例 |
| 複数の列でまとめる | `df.groupby(["日付", "店舗"])["売上"].sum()` |
| 添字を列に戻す | `.reset_index()` を付ける |
| クロス集計 | `df.pivot_table(index="日付", columns="店舗", values="売上", aggfunc="sum")` |
| 集計結果を元の行数のまま足す | `df.groupby("店舗")["売上"].transform("sum")` |
| 縦横を入れ替える | `df.melt(id_vars=["日付"])` / 戻すのは `df.pivot(...)` |

```python
# 列に名前を付けて集計する (named aggregation)
df.groupby("path").agg(
    件数=("dur", "size"),
    平均秒=("dur", "mean"),
    最遅秒=("dur", "max"),
).reset_index()
```

> [!TIP]
> `groupby` の結果は添字 (index) になります。**そのまま次の工程に渡すと
> 列が見つからないと言われます。** `.reset_index()` で普通の列に戻します。

## 結合

| | |
|---|---|
| 左の行を全部残す | `df.merge(other, on="id", how="left")` |
| 両方にある行だけ | `df.merge(other, on="id", how="inner")` |
| 列名が違う | `df.merge(other, left_on="社員番号", right_on="id")` |
| どちら由来か印を付ける | `df.merge(other, on="id", how="left", indicator=True)` |
| 縦に積む | `pd.concat([df1, df2], ignore_index=True)` |
| 横に並べる | `pd.concat([df1, df2], axis=1)` |

> [!WARNING]
> **`merge` は行数を変えます。** 右側に同じキーが2行あれば、左の1行が2行に増えます。
> `len(df)` を前後で比べる癖を付けます。増えていたら右側のキーが重複しています
> (`other["id"].duplicated().sum()` で分かります)。
> `indicator=True` を付けると `_merge` 列に `left_only` / `both` が入るので、
> 結合できなかった行を数えられます。

## よくある落とし穴

| | |
|---|---|
| 欠損があって `astype("int64")` が落ちる | `Int64` (大文字) を使います |
| `.str` を忘れる | 文字列の操作は必ず `s.str.xxx()` です |
| `and` / `or` を書いて落ちる | 列同士は `&` と `\|`、しかも各条件を括弧で囲みます |
| `SettingWithCopyWarning` が出る | 絞った結果に代入しています。`df.loc[条件, "列"] = 値` か `.copy()` |
| `merge` のあと行が増えた | 右側のキーが重複しています |
| `groupby` の結果で列が見つからない | 添字になっています。`.reset_index()` |
| tz-aware と tz-naive を比べて落ちる | `tz_localize` / `tz_convert` で揃えます |
| `df["a"][0] = 1` が効かない | 元に反映されません。`df.loc[0, "a"] = 1` |
| CSV に書いたら型が消えた | CSV に型はありません。Parquet を使います |
| 表示が途中で `...` になる | `pd.set_option("display.max_columns", None)` |

---

## この表の使い方

クエストで詰まったら、**まず「まず形を見る」を全部やってから**該当する節を引きます。
何が汚れているか分からないまま直そうとすると、直す先を間違えます。

| | |
|---|---|
| [quest-02](quest-02-access-log-transform/) | 「型を直す」「文字列」 |
| [quest-01](quest-01-raw-ingest/) | 「読む / 書く」「欠損」「重複」「結合」 |
