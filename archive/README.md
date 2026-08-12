# archive — 試したが採らなかったもの

**ノートブックで Python だけでなく SQL も書けるようにする、という検討の記録です。**
結論としては採用しませんでした。ここに置いてあるのは、その過程で作った動くパイロットと、
やめた理由です。

判断そのものより**なぜそう判断したか**のほうが後から効くので、数字も一緒に残しています。

## 動機と結論

ドリルの `sql-01` は DuckDB を使いますが、SQL は Python の文字列として書いています。

```python
def q(sql):
    return con.sql(sql).df()

q('''
SELECT count(*) AS n FROM orders WHERE customer_id IS NULL
''')
```

これを「セルにそのまま SQL を書ける」形にできないか、というのが出発点でした。

**最終的には、そもそもノートブックで SQL をやる必要が無い、という結論になりました。**
SQL はノートブック以外でいくらでも書けます。ノートブックを使った学習は
Python(pandas / Spark / Polars)に寄せることにしました。

## 試した3つ

| 案 | 追加パッケージ | 最終リリース | SQLハイライト | `assert` 同居 |
| --- | --- | --- | --- | --- |
| 現状の `q('''...''')` | 0 | — | なし | できる |
| marimo | +14 | 2026 | あり(SQLセル) | できない |
| magic-duckdb `%%dql` | +1 | 2026-01 | 別途要 | できない |
| JupySQL `%%sql` | +13 | 2025-03 | 別途要 | できない |
| jupyterlab-sql-editor | +49 | — | あり(Python文字列も) | 影響なし |

### 共通してぶつかった壁

**セルマジックもSQLセルも、セル全体を食います。** ドリルのミニ練習は

```python
ans = q('''...''')
assert ans["n"].iloc[0] == 1
print("OK")
```

という形で、**クエリと `assert` が同じセルに居る必要があります**。
セル全体が SQL になる方式では、この形が作れません。

結果としてどの案でも「見比べはSQLセル、ミニ練習は `q()`」という
**書き方が2種類混ざる**形になります。これが最後まで解消できませんでした。

## marimo

`sql-01` を移植したものが [sql-01-marimo.py](sql-01-marimo.py) です。動きます。
見比べ25セルを SQL セルにし、ミニ練習16問は `q()` のまま残しました。
答えを流し込むと16問すべて通ります。

採らなかったのは、**ドリル全体やチュートリアルに広げるときの対価**が見合わなかったためです。

| 対価 | 中身 |
| --- | --- |
| 変数の一括改名 | marimo は同名変数の複数セル定義を禁止します。`ans` が6本で163箇所、`a` / `b` / `s` なども含めて約140箇所を `_ans` のようなセルローカル名に変える必要があります |
| 循環代入の解消 | `tutorial-01` の `old2 = old2.assign(...)` は marimo では循環になります。節をまたいで変数を1つ増やす、という教材本文に踏み込む改変が要ります |
| パス解決の分岐 | VS Code 拡張はリモートやコンテナのカーネルに繋げないので、`/data` 直書きをやめて Docker / ホスト / VS Code の3経路で解決する分岐が要ります |
| 検証の足場 | 変換と検証に `marimo._ast.codegen` や `app._cell_manager` といった**非公開API**を使うことになり、marimo の更新で黙って壊れます |

**教材の中身を変えずには移行できない**、というのが決め手でした。

### 副産物: 日本語コメントで依存解析が落ちる

marimo が依存を解析する `find_sql_defs` は、**SQLコメントに日本語が入るとバイト長と文字長がずれて
`IndexError` になります**(duckdb 1.1.3)。`CREATE TABLE` のセルで起きるとテーブル名が
marimo の変数として登録されず、依存追跡が黙って壊れます。
`sql-01-marimo.py` では、`CREATE` セルの説明をマークダウンセルに追い出して回避しています。

## JupySQL

**入れていません。** 調べた段階で見送りました。

- `%%sql` セルに `assert` を置けないので、marimo と同じ混在が起きます
- **SQLのハイライトは付いてきません。** JupyterLab 4 は `%%sql` を色分けしません。
  別拡張が要り、それが `jupyterlab-sql-editor` で **+49パッケージ**
  (pylint / black / yapf / python-lsp-server まで引き込みます)
- SQLAlchemy と、テレメトリ(`posthog` / `ploomber-core`)が付いてきます

**「マジックを入れれば SQL が色分けされる」わけではない**、というのがいちばんの発見でした。

## magic-duckdb

[sql-01-dql.ipynb](sql-01-dql.ipynb) が `%%dql` に置き換えた版です。動きます。

```
%%dql
-- A: = NULL
SELECT count(*) AS n FROM orders WHERE customer_id = NULL
```

**3つの中では一番筋が良い案でした。**

- 追加パッケージは `magic-duckdb` **1つだけ**(95 → 96)。`duckdb` も含めバージョンは1つも動きません
- `%dql -co con` で**既存の接続をそのまま使えます**。`CREATE TABLE` 済みの `con` が見えます
- VSCode 対応を明記しています
- セットアップセルに2行足して、見比べ25セルを変換しただけです。
  変数の改名もパスの可搬化も要りませんでした

見比べセルの結果を答え合わせの数字と13点突き合わせ、すべて一致しています
(`= NULL` は0件 / `IS NULL` は1件、`INNER` 10行 / `LEFT` 12行、`rank` の同順位 `[1,2,2,4]` など)。

採らなかったのは技術的な理由ではなく、**そもそもノートブックで SQL をやらない**と決めたためです。

## 副産物: sql-01 の 3-4 節に誤りがあります

**これは本体に残っている課題です。** 検証中に見つけました。

`drills/notebooks/sql-01-null-join-window.ipynb` の 3-4 節「NULLS LAST」の答え合わせは
こう書いています。

> DuckDB と PostgreSQL の既定は「`ASC` なら NULL は最後、`DESC` なら最初」です。

**PostgreSQL では正しく、DuckDB では誤りです。**
DuckDB 1.1.3 の `default_null_order` は向きに関係なく `nulls_last` 固定です。
そのため A と B が同じ結果になり、見比べになっていません。

```
A:  ORDER BY amount DESC              → [4800, 4800, 3600, 2400]
B:  ORDER BY amount DESC NULLS LAST   → [4800, 4800, 3600, 2400]   同じ
```

節の狙い(「書いておけばどこでも同じ結果になる」)を活かすなら、
B を `NULLS FIRST` にすると差が出ます。

```
B案: ORDER BY amount DESC NULLS FIRST → [NaN, 4800, 4800, 3600]
```

## ここのファイルについて

**そのままでは動きません。** どちらも CSV を `/data/orders.csv` のように直書きしていて、
これは `drills` のコンテナにマウントされるパスです。動かすなら `drills/work/` に置いて
`drills` のコンテナから開いてください。`sql-01-marimo.py` には `marimo`、
`sql-01-dql.ipynb` には `magic-duckdb` も要ります。どちらも今は依存から外してあります。

| | |
| --- | --- |
| [sql-01-marimo.py](sql-01-marimo.py) | marimo 版。SQLセル31 / Pythonセル21 / マークダウン52 |
| [sql-01-dql.ipynb](sql-01-dql.ipynb) | `%%dql` 版。見比べ25セルを変換したもの |
