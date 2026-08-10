# drills — SQL と pandas の基礎ドリル

クエストに入る前の準備運動。**引数ひとつで結果が変わるところ**だけを集めた
ノートブック集。

データエンジニアリングで書くコードは、実務では大半が SQL か pandas になる。
その2つで「知らないと黙って間違う」ところを、小さいデータで一つずつ潰す。

## 使い方

```bash
./start.sh
```

http://localhost:8888/lab が開く。左のファイルブラウザからノートブックを開く。

```bash
./stop.sh                # 止める
./start.sh --reset       # ノートブックを配り直す (自分の書き込みは消える)
```

| | |
| --- | --- |
| `notebooks/` | 配布用のノートブック。git管理 |
| `work/` | **自分がいじるほう。git管理外** |
| `data/` | 12行のCSVが3つ。全部目で見られる大きさ |

`start.sh` が `notebooks/` の中身を `work/` に配る。
**既にあるファイルは上書きしない**ので、書きかけが消えることはない。

## 進め方

各節はこの形になっている。

```
### 2-1. keep_default_na
   説明

   [セルA]  ← 実行する前に、どうなるか予想する
   [セルB]

   <details>何が起きたか</details>   ← 予想してから開く
```

**予想せずに実行すると、ほとんど身に付かない。**
予想と違ったところが、自分がまだ知らないところ。

各ノートブックの最後に練習問題がある。`assert` が通れば正解。

## 収録

| | テーマ | 主な内容 | |
| --- | --- | --- | --- |
| pandas-01 | 読み込みと型 | `dtype` / `keep_default_na` / `na_values` / `thousands` / `astype` vs `to_numeric` / `int64` vs `Int64` / `to_datetime(format=)` / `.dt.date` / `NaN` の比較 | できた |
| pandas-02 | 選ぶ・絞る・変える | `[]` vs `[[]]` / `.loc` vs `.iloc` / `&` と括弧 / `isin` `between` `query` / 連鎖indexing / `assign` / `map` vs `apply` vs `.str` / `where` vs `mask` / `replace` vs `str.replace` | できた |
| pandas-03 | 集約・重複・並べ替え | `as_index` / `dropna` / `size` vs `count` / named agg / `transform` / **`.last()` の罠** / `drop_duplicates` / `duplicated(keep=)` / `na_position` / `rank(method=)` | できた |
| sql-01 | NULL・JOIN・窓関数 | 三値論理 / `NOT IN` の罠 / `count(*)` vs `count(col)` / `GROUP BY` と NULL / `ON` vs `WHERE` / 1対多の水増し / ANTI JOIN / `row_number` vs `rank` / `QUALIFY` / `NULLS LAST` | できた |
| pandas-04 | 結合と連結 | `merge` の `how` / `on` vs `left_on` / `suffixes` / `indicator` / `validate` / `concat` の `axis` `join` `ignore_index` / index の罠 | これから |
| sql-02 | 集約と日付 | `CTE` vs サブクエリ / `GROUPING SETS` / 日付関数 / `date_trunc` / `generate_series` で日付を埋める | これから |
| pandas-05 | 時系列 | `resample` / `rolling` / `shift` / タイムゾーン | これから |

## 特に効くところ

初めてなら、この3つだけでも先に見ておくと quest で詰まりにくい。

| | 何が起きるか |
| --- | --- |
| pandas-01 `1-1` | 型を推測させると、金額が文字列のまま集計される |
| pandas-03 `3-1` | `groupby().last()` が**どの行にも存在しない行**を作る |
| sql-01 `2-2` | `LEFT JOIN` の条件を `WHERE` に書くと `INNER` に化ける |

## データ

3ファイル、合計23行。すべて `data/` にあり、直接読める。

```
orders.csv     12行   注文。欠損・カンマ区切り・大文字混在を少しずつ含む
customers.csv   5行   顧客。1人は注文が無い
payments.csv    5行   支払い。1つの注文に2件、存在しない注文に1件
```

**小さいので全部目で見られる。** 集計結果が合っているかを手で数えて確かめられる、
というのがこの大きさにしてある理由。
