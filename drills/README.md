# drills — SQL と pandas の基礎ドリル

クエストに入る前の準備運動です。小さいデータで、よく使う書き方を一つずつ試します。

データエンジニアリングで書くコードは、実務では大半が SQL か pandas になります。
その2つを、**説明を読む → セルを実行する → ミニ練習を1問解く**の繰り返しで進めます。

## 使い方

```bash
./start.sh
```

http://localhost:8888/lab が開きます。左のファイルブラウザからノートブックを開いてください。

```bash
./stop.sh                # 止める
./start.sh --reset       # ノートブックを配り直す (自分の書き込みは消える)
```

| | |
| --- | --- |
| `notebooks/` | 配布用のノートブック。git管理 |
| `work/` | **自分がいじるほう。git管理外** |
| `data/` | 小さなCSVが5つ。全部目で見られる大きさ |

`start.sh` が `notebooks/` の中身を `work/` に配ります。
**既にあるファイルは上書きしない**ので、書きかけが消えることはありません。

## どこから読むか

**pandas を触ったことがないなら `pandas-00` から。**
「pandas でやることは結局この10個」を、SQL の `SELECT` 文と対応づけて一通り見ます。
引っかけは無く、素直な説明とミニ練習だけです。

10個が手に馴染んだら `pandas-01` 以降へ。ここからは
**引数ひとつで結果が変わるところ**を A と B で並べて見比べる形になります。

```
pandas-00  基本の10個            ← 素直な説明
   ↓
pandas-01  読み込みと型          ← ここから A/B で見比べる形式
pandas-02  選ぶ・絞る・変える
pandas-03  集約・重複・並べ替え
sql-01     NULL・JOIN・窓関数
```

## 進め方

各節はこの形になっています。

```
### 2-1. keep_default_na
   説明 (2〜3行)

   [セルA]  ← 実行する
   [セルB]  ← 引数を1つ変えたもの

   <details>答え合わせ</details>

   ミニ練習 (1問)
   <details>答え</details>
```

セルAとBは、実行する前に「どこが変わりそうか」を一言だけ思い浮かべてから
実行すると記憶に残ります。外れて当たり前なので、気楽にどうぞ。

**ミニ練習は「列の名前を変えるだけ」「条件を1つ変えるだけ」くらいの軽さ**です。
`assert` が通れば `OK` と出ます。すぐ下に答えが付いているので、
分からなければ開いて写して動かすだけでも十分です。

各ノートブックの最後には、組み合わせて書く「仕上げ」が3問あります。
こちらにも答えが付いています。

## 収録

| | テーマ | 主な内容 | |
| --- | --- | --- | --- |
| **pandas-00** | **まずはこの10個** | DataFrame と Series / 読む・見る / `SELECT` `WHERE` `ORDER BY` `GROUP BY` `JOIN` `UNION` `DISTINCT` に対応する10個 / メソッドチェーン | できた |
| pandas-01 | 読み込みと型 | `dtype` / `keep_default_na` / `na_values` / `thousands` / `astype` vs `to_numeric` / `int64` vs `Int64` / `to_datetime(format=)` / `.dt.date` / `NaN` の比較 | できた |
| pandas-02 | 選ぶ・絞る・変える | `[]` vs `[[]]` / `.loc` vs `.iloc` / `&` と括弧 / `isin` `between` `query` / 絞ってから代入 / `assign` / `map` vs `apply` vs `.str` / `where` vs `mask` / `replace` vs `str.replace` | できた |
| pandas-03 | 集約・重複・並べ替え | `as_index` / `dropna` / `size` vs `count` / named agg / `transform` / **`.last()` の罠** / `drop_duplicates` / `duplicated(keep=)` / `na_position` / `rank(method=)` | できた |
| sql-01 | NULL・JOIN・窓関数 | 三値論理 / `NOT IN` の罠 / `count(*)` vs `count(col)` / `GROUP BY` と NULL / `ON` vs `WHERE` / 1対多の水増し / ANTI JOIN / `row_number` vs `rank` / `QUALIFY` / `NULLS LAST` | できた |
| pandas-04 | 結合と連結 | `merge` の `how` / `on` vs `left_on` / `suffixes` / `indicator` / `validate` / `concat` の `axis` `join` `ignore_index` / index の罠 | これから |
| sql-02 | 集約と日付 | `CTE` vs サブクエリ / `GROUPING SETS` / 日付関数 / `date_trunc` / `generate_series` で日付を埋める | これから |
| pandas-05 | 時系列 | `resample` / `rolling` / `shift` / タイムゾーン | これから |

## 特に効くところ

急いでいるなら、この3つだけでも先に見ておくと quest で詰まりにくくなります。

| | 何が起きるか |
| --- | --- |
| pandas-01 `1-1` | 型を推測させると、金額が文字列のまま集計される |
| pandas-03 `3-1` | `groupby().last()` が**どの行にも存在しない行**を作る |
| sql-01 `2-2` | `LEFT JOIN` の条件を `WHERE` に書くと `INNER` のようになる |

## データ

5ファイル、合計38行。すべて `data/` にあり、直接開いて読めます。

```
pandas-00 用 (きれい。汚れの話を混ぜない)
  sales.csv     12行   売上。3店舗 x 3商品
  shops.csv      4行   店。1店は売上が無い (JOIN の説明用)

pandas-01 以降 (汚れを少しずつ含む)
  orders.csv    12行   注文。欠損・カンマ区切り・大文字混在
  customers.csv  5行   顧客。1人は注文が無い
  payments.csv   5行   支払い。1つの注文に2件、存在しない注文に1件
```

集計結果が合っているかを手で数えて確かめられる、というのがこの大きさにしてある理由です。
