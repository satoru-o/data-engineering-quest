# 付録. 「やりたいことが書けない」を抜ける

やることは分かっているのにコードにならない、という状態のための章。
データエンジニアリングの話ではなく、**手の動かし方**の話。

## 「書けない」の正体は3つ

| | 症状 | 効く対策 |
| --- | --- | --- |
| **語彙がない** | やりたいことに名前が付いていることを知らないので、検索もできない | 語彙表を引く。`dir()` で探す |
| **粒度が大きい** | 「CSVを整形する」を一息で書こうとしている | 手順に割る。1手順=1行 |
| **反応が遅い** | 全部書いてから実行するので、どこで間違えたか分からない | REPLで1行ずつ |

だいたいは3番目が根本原因になっている。**書けないのではなく、書いたものを確かめる速度が遅い**。
最初にここを直す。

---

## 1. 対話的にやる。スクリプトは最後に書く

一番効くのがこれ。ファイルに書いて実行、を繰り返してはいけない。

```bash
./repl.sh
```

IPythonが立ち上がり、`pd` などが読み込まれた状態で始まる。ここで1行ずつ試す。

```python
In [1]: df = pd.read_csv(FILES[0], dtype=str, keep_default_na=False)
In [2]: df.head()
In [3]: df["quantity"].unique()
```

**動いた行だけを `work/ingest.py` に写す。** これが基本の進め方。
「書く → 実行 → エラー」ではなく「試す → 動いた → 記録する」。

REPLでは変数が残るので、途中からやり直せる。
1200行の読み込みを毎回待たされることもない。

### スクリプトの途中から対話に落ちる

書き途中のコードのど真ん中で止めて、その場の変数を触れる。

```python
def clean(df):
    df = df.map(norm)
    breakpoint()          # ここで止まってIPythonに落ちる
    ...
```

`breakpoint()` を置いて `./run.sh`。その時点の `df` を好きに触れる。
`c` で続行、`q` で終了。**print文を仕込むより速い。**

---

## 2. 日本語で手順を書いてから、1行ずつ埋める

やりたいことを日本語のまま、コメントで並べる。

```python
def clean(df):
    # 1. 欠損表現を null にする
    # 2. 全角を半角にする
    # 3. 日付を date にする
    # 4. 金額を int にする
    # 5. order_id ごとに ingested_at 最新の行だけ残す
    # 6. 除外する
    # 7. order_id で並べる
    return df
```

quest-01なら `spec/orders.md` の「処理」節がそのまま設計書になっている。**写すだけでよい。**

ここから、**書ける行だけ**埋める。書けない行は飛ばして次に行く。

```python
    # 1. 欠損表現を null にする
    # 2. 全角を半角にする
    # 3. 日付を date にする
    df["order_date"] = ...        ← ここだけ書けた
    # 4. 金額を int にする
```

7つ全部が埋まらないと動かない、ということはない。
**常に「動く状態」を保ったまま、1つずつ埋めていく。**

出力の行数が合わなくても、型が違っても、
`out/report.txt` は「どこまで来たか」を返してくれる。1行埋めるごとに `./run.sh` してよい。

---

## 3. 語彙表 — 日本語のやりたいこと → 検索語

**検索できないのは、名前を知らないから。** ここが最大の壁。
「pandas やりたいこと」で検索しても出てこないが、
「pandas drop_duplicates」なら一発で公式ドキュメントに着く。

### 行を操作する

| やりたいこと | 呼び名 | 検索語 |
| --- | --- | --- |
| 縦にくっつける | 連結 / concatenate | `pandas concat` |
| 横にくっつける | 結合 / join | `pandas merge` |
| 条件に合う行だけ残す | フィルタ | `pandas filter rows by condition` |
| 重複を消す | 重複排除 / dedup | `pandas drop_duplicates keep last` |
| 重複を探す | | `pandas duplicated` |
| 並べ替える | ソート | `pandas sort_values` |
| グループごとに集計する | 集約 / aggregate | `pandas groupby agg` |
| グループごとに1行選ぶ | | `pandas groupby first row` |
| 行数を数える | | `len(df)` / `df.shape` |

### 列を操作する

| やりたいこと | 呼び名 | 検索語 |
| --- | --- | --- |
| 列を選ぶ・並べ替える | 射影 / projection | `df[["a", "b"]]` |
| 列の名前を変える | | `pandas rename columns` |
| 列を消す | | `pandas drop columns` |
| 列を追加する | | `df["new"] = ...` |
| 型を変える | キャスト / cast | `pandas astype` |

### 値を1つずつ変換する

| やりたいこと | 呼び名 | 検索語 |
| --- | --- | --- |
| 1列の全要素に関数を適用 | 写像 / map | `pandas Series map` |
| 全列・全要素に適用 | | `pandas DataFrame map applymap` |
| 文字列操作をまとめて | ベクトル化文字列操作 | `pandas str accessor` |
| 前後の空白を取る | トリム / strip | `pandas str strip` |
| 小文字にする | | `pandas str lower` |
| 置換する | | `pandas str replace regex` |
| 対応表で置き換える | | `pandas replace dict` |
| 欠損かどうか | | `pandas isna notna` |
| 欠損を埋める | | `pandas fillna` |
| 文字列を日付にする | パース / parse | `pandas to_datetime format` |
| 文字列を数値にする | | `pandas to_numeric errors` |
| 全角を半角にする | Unicode正規化 | `python unicodedata normalize NFKC` |

### 中身を調べる

| やりたいこと | 検索語 / コード |
| --- | --- |
| 最初の数行 | `df.head()` |
| 型の一覧 | `df.dtypes` |
| **列に入っている値の種類を全部** | **`df["col"].unique()`** |
| 値ごとの件数 | `df["col"].value_counts()` |
| 欠損の数 | `df.isna().sum()` |
| 統計の要約 | `df.describe()` |

**`unique()` が最強。** 汚れたデータを扱うときは、まずこれを叩く。

```python
In [3]: sorted(df["quantity"].unique())
Out[3]: ['', '-', '-1', '-３', '0', '1', '10', '2', ..., 'NULL', '０', '１', '２', ...]
```

「この列にどんな汚れがあるか」を推測する必要がなくなる。**全部見える。**
仕様書を読んで想像するのではなく、データに聞く。

---

## 4. 名前を思い出せないときの探し方

### `dir()` + 部分一致

「重複を消すやつ、なんて名前だっけ」

```python
In [4]: [m for m in dir(df) if "dup" in m]
Out[4]: ['_check_inplace_and_allows_duplicate_labels', 'drop_duplicates', 'duplicated']
```

思い出せそうな断片(`dup`, `sort`, `merge`, `na`)を入れて絞る。
**検索エンジンより速い。**

文字列操作なら `df["col"].str` の下を見る。

```python
In [5]: [m for m in dir(df["amount"].str) if not m.startswith("_")]
```

### `?` でその場でドキュメント

IPythonなら、末尾に `?` を付けると説明が出る。

```python
In [6]: df.drop_duplicates?
```

`??` ならソースまで出る。ブラウザに移らなくてよいので、流れが切れない。

### タブ補完

`df.dr` まで打って `Tab`。候補が出る。
**名前を全部覚える必要はない。頭2〜3文字だけ覚えておけばよい。**

---

## 5. 検索の作法

- **英語で検索する。** 日本語の記事は数が少なく、バージョンが古い。
  `pandas drop duplicates keep last` のように、単語を並べるだけでよい
- **公式ドキュメントを最優先。** `pandas.pydata.org` が上位に出たらそれを開く。
  個人ブログは pandas 1.x 時代の書き方が残っていることが多い
- **「たぶんある」と思って探す。** pandas は API が非常に広い。
  自分で `for` ループを書き始めたら、たいてい探し方が足りていない
- **エラーは最後の行から読む。** 上のスタックトレースはほぼライブラリの内部。
  最終行の `ValueError: ...` だけが自分に関係する

```
ValueError: invalid literal for int() with base 10: 'NULL'
```

この1行に「int にしようとした」「`'NULL'` という文字列で失敗した」が全部書いてある。
**エラーメッセージは検索するより先に読む。**

---

## 6. AIに聞くときの聞き方

聞くこと自体は良い。**聞き方で、身に付くかどうかが変わる。**

| 良くない | 良い |
| --- | --- |
| 「ingest.py を書いて」 | 「この列にこういう値が入っている(貼る)。全角数字を半角にしたい。pandasで」 |
| 「動きません」 | 「このコードで、このエラーが出る(両方貼る)」 |
| 完成品をもらう | **1ステップぶんをもらう** |

そして**受け取ったあとが本番**。

1. 出てきたメソッド名を控える(例: `str.normalize` ではなく `unicodedata.normalize` だった)
2. その名前で**公式ドキュメントを引き直す**
3. REPLで、引数を変えて動かしてみる

これをやると、次から自分で書ける。写経して次に進むと、次も同じところで止まる。
**答えではなく語彙をもらう**、という使い方が一番効く。

---

## 7. 1手ごとの確認の型

1行書いたら、必ずこの3つを見る。

```python
len(df)        # 行数は意図どおりか
df.dtypes      # 型は変わったか
df.head()      # 中身はどうなったか
```

**特に行数。** 意図せず行が減っている/増えているのが、データ処理で最も多い事故。

```python
In [7]: len(df)
Out[7]: 1290

In [8]: df = df.drop_duplicates(subset="order_id", keep="last")

In [9]: len(df)
Out[9]: 1200          ← 90件減った。重複していたのは90件のはず。合っている
```

**減った数に説明が付くか**を毎回確認する。「なんとなく減った」を通すと、後で必ず数字が合わなくなる。

---

## 8. 小さく試す

1200行で試さない。**20行で挙動を確かめてから**全体に適用する。

```python
In [10]: s = df["amount"].head(20)
In [11]: s.map(parse_amount)
```

さらに小さく、値1個で。

```python
In [12]: parse_amount("￥1,200")
```

関数が正しいかを、DataFrameを通さずに確かめる。
**「関数が悪いのか、適用の仕方が悪いのか」を切り分ける**のが目的。

---

## 実際の流れ(quest-01の `quantity` を例に)

```python
In [1]: df = pd.read_csv(FILES[1], dtype=str, keep_default_na=False)

# まず何が入っているか見る
In [2]: sorted(df["quantity"].unique())
Out[2]: ['', '-', '-1', '-３', '0', '1', '10', '2', '3', ..., 'NULL', '０', '１', '２', ...]

# 素直にintにしてみる。だめでもいい。だめな理由が知りたい
In [3]: df["quantity"].astype(int)
ValueError: invalid literal for int() with base 10: 'NULL'

#   → 'NULL' が邪魔。全角数字もある。この2つを先に片付ける必要がある、と分かった
#   → 「全角を半角に」は何という操作か? → 語彙表 → unicodedata.normalize

In [4]: unicodedata.normalize("NFKC", "３")
Out[4]: '3'

# 効いた。列全体に適用する。「列全体に関数を」は? → 語彙表 → map
In [5]: q = df["quantity"].map(lambda s: unicodedata.normalize("NFKC", s))

In [6]: sorted(q.unique())
Out[6]: ['', '-', '-1', '-3', '0', '1', '10', '2', ..., 'NULL']

#   → 全角が消えた。残るのは '', '-', 'NULL' と 0以下。ここからは仕様の話
```

**推測していない。** 毎回データに聞いて、返ってきたものを見て次を決めている。
これができるようになると、知らないライブラリでも進めるようになる。

---

## まとめ

1. `./repl.sh` で1行ずつ試す。スクリプトは動いた行の記録
2. 手順を日本語で並べて、書ける行から埋める
3. `unique()` でデータに聞く。推測しない
4. 名前が出てこなければ `dir()` の部分一致と `?`
5. 英語で、公式ドキュメントを引く
6. AIには答えではなく語彙をもらう
7. 1手ごとに `len` / `dtypes` / `head`
8. 20行で試してから1200行へ
