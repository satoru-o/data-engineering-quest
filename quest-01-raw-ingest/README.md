# quest-01: raw-ingest

汚れた生データを、下流が信用できるテーブルに変える。

> 前提の読み物: [docs/01](../docs/01-what-is-data-engineering.md) / [docs/03](../docs/03-dirty-data.md)

## 状況

社内の注文データをBIから使いたい、という話が来た。
生データはCSVで `data/` に届いている。あとは読んで書くだけ……のはずだった。

送信元のシステムが複数ある。ファイルによって**文字コードが違い、列の並びが違い、
日付と金額の書き方が違う**。しかも遅れて届くファイルには、既に届いた注文の
**訂正**が混ざっている。

送信元は直してもらえない。取り込み側で吸収するしかない。

## ミッション

`spec/orders.md` の仕様どおりに `out/orders.parquet` を作る。

見張り役が10秒ごとに出力を検証していて、**すべて合格している間だけ**
`out/flag.txt` が現れる。

## 手順

```bash
./setup.sh              # 生データを作り、見張り役を起動する
cat spec/orders.md      # 出力仕様を読む
head -3 data/*.csv      # 生データを自分の目で見る

# work/ingest.py を書く
./run.sh                # 実行する
./verify.sh --status    # 見張り役の判定を見る

cat out/flag.txt
./verify.sh 'FLAG{...}'
```

`./setup.sh` が `skeleton/ingest.py` を `work/ingest.py` に配るので、そこに書く。
pandasでもDuckDBのSQLでも、Parquetが仕様どおりに出れば何で書いてもよい。

> [!NOTE]
> **`work/` はgit管理外。** 自分の答えがコミットされることはない。
> `setup.sh` は既にあるファイルを上書きしないので、何度叩いても書きかけは消えない。
> 雛形からやり直したいときは `cp skeleton/ingest.py work/ingest.py`。

対話的にいじりたいときはコンテナに入る。

```bash
./shell.sh
```

| コンテナの中 | |
| --- | --- |
| `/data` | 生データ(読み取り専用) |
| `/work` | 自分のコード(ホストの `work/` と同じ) |
| `/out` | 出力先 |

pandas / pyarrow / duckdb が入っている。

## 判定

`out/report.txt` に、どのチェックが落ちたかが書かれる。上から順に見ていけばよい。

```
=== 05:51:20  すべて合格 ===
列 … OK
型 … OK
order_idの一意性 … OK
並び順 … OK
行の集合 … OK (1145 行)
order_date … OK
...
```

不一致があれば、実際の値と期待する値が数件ぶん出る。

```
amount_jpy … NG  312 行が不一致
    ORD-000037  実際: 1  期待: 9800
```

> [!NOTE]
> **チェックは上から順に、落ちた時点で打ち切られる。**
> 列が合っていないうちは行数のことは教えてくれない。1つずつ潰していく。

---

## 診断の型

取り込みは、**上流を疑う順番**が決まっている。

| 段 | 問い | 落ちるとどうなるか |
| --- | --- | --- |
| 1 | そもそも読めるか | 例外で止まる。**まだ良い方** |
| 2 | 読めたとして、正しく読めているか | 文字化け。**黙って通る** |
| 3 | 列は揃っているか | 列がずれる、`NaN` が増える |
| 4 | 値は意図した型になっているか | 文字列のまま集計されて0になる |
| 5 | 行の粒度は正しいか | 重複、二重計上 |
| 6 | 落とすべき行を落としているか | 汚れが下流に流れる |

**2段目が一番こわい。** 例外が出ないので、気づかないまま下流に流れる。

<details>
<summary>ヒント1: 1段目で止まる</summary>

`./run.sh` を叩くと、まず `UnicodeDecodeError` で止まるはず。

```
UnicodeDecodeError: 'utf-8' codec can't decode byte 0x94 in position 92
```

どのファイルで止まったかを見る。全ファイルが同じ文字コードとは限らない。

```bash
file -b --mime-encoding data/*.csv
```

日本のシステムから来るCSVは、いまだにCP932(いわゆるShift_JIS)であることがある。
読めなかったら別の文字コードで読み直す、という素直な作りでよい。

> ここで `errors="ignore"` や `errors="replace"` で握りつぶすと、例外は消えるが
> 顧客名が壊れる。**2段目に落ちる**。例外は消すのではなく、正しく読む。
</details>

<details>
<summary>ヒント2: 列の並びに依存しない</summary>

ファイルによって列の順番が違う。

```bash
head -1 data/*.csv
```

位置で取らず、名前で取る。`pd.concat` は列名で揃えてくれるので、
`dtype=str` で読んで結合すれば自然にそうなる。
</details>

<details>
<summary>ヒント3: 表記ゆれは、まず正規化してから解釈する</summary>

`３`(全角数字)や `￥`(全角円記号)や `　`(全角空白)は、
一つずつ場当たりに置換すると必ず漏れる。先に**Unicode正規化**を通す。

```python
import unicodedata
unicodedata.normalize("NFKC", s)
```

NFKCは「互換文字を標準の形に潰す」正規化で、全角英数字・全角記号・全角空白が
まとめて半角側に寄る。**日本語のデータを扱うなら最初に入れる一手**。

そのあとで `strip()` → 欠損表現の判定 → 型変換、の順に進める。
</details>

<details>
<summary>ヒント4: pandasの落とし穴(重複排除)</summary>

「`order_id` ごとに `ingested_at` が最新の行」を取るとき、
これは**間違い**。

```python
df.sort_values("ingested_at").groupby("order_id").last()   # NG
```

`GroupBy.last()` は「グループの最後の行」ではなく、**列ごとに最後の非null値**を返す。
最新行の `amount` が欠損だと、こっそり古い行の `amount` を拾ってしまう。
仕様の5(除外)が効かなくなり、落とすべき注文が生き残る。

行そのものを1本選ぶ。

```python
df.sort_values("ingested_at").drop_duplicates(subset="order_id", keep="last")
```

DuckDBなら素直に書ける。

```sql
SELECT * FROM (
  SELECT *, row_number() OVER (PARTITION BY order_id ORDER BY ingested_at DESC) AS rn
  FROM raw
) WHERE rn = 1
```
</details>

<details>
<summary>ヒント5: 型は最後に固める</summary>

`pa.Table.from_pandas(df, schema=SCHEMA)` はスキーマに合わない列があると落ちる。
落ちてくれるのは良いことで、これが**データ契約**の最小形になっている。

`date32` は Python の `datetime.date` から作る。`pd.Timestamp` のままだと
`timestamp[ns]` になって型チェックに落ちる。

`quantity` は `int32`。欠損を含む列を `astype("int32")` すると落ちるので、
除外を済ませてから型を固める。
</details>

---

## コマンド集

### 生データを覗く

```bash
file -b --mime-encoding data/*.csv     # 文字コード
head -1 data/*.csv                     # 列の並び
wc -l data/*.csv                       # 行数

# CP932のファイルをターミナルで読む
iconv -f cp932 -t utf-8 data/orders_2024-01-21_2024-01-31.csv | head -5
```

### DuckDBで探索する

`./shell.sh` で入ってから `duckdb`。CSVを直接クエリできる。

```sql
-- 表記のバリエーションを数える
SELECT order_date, count(*) FROM read_csv('/data/orders_*.csv', all_varchar=true)
GROUP BY 1 ORDER BY 2 DESC LIMIT 20;

-- 重複している order_id
SELECT order_id, count(*) c FROM read_csv('/data/*.csv', all_varchar=true)
GROUP BY 1 HAVING c > 1 LIMIT 10;

-- 書いたParquetを確認する
DESCRIBE SELECT * FROM '/out/orders.parquet';
SELECT count(*), sum(amount_jpy) FROM '/out/orders.parquet';
```

`all_varchar=true` が大事。DuckDBに型を推測させると、**汚れが推測で埋められて見えなくなる**。
生データを調べるときは全部文字列で読む。

### 出力を確認する

```bash
./run.sh python -c "
import pyarrow.parquet as pq
t = pq.read_table('/out/orders.parquet')
print(t.schema)
print(t.num_rows)
print(t.slice(0, 5).to_pandas())
"
```

## 後片付け

```bash
./teardown.sh
```

`work/` の自分のコードは残る。生データと出力は消える。

## 補足

- `./setup.sh` を叩き直すと**生データもFLAGも作り直される**。答えを覚えることはできない
- FLAGは見張り役がメモリ上に持っていて、合格している**間だけ**書き出す。1回通しただけでは残らない
- 正解の行数は毎回変わる。他人の答えも、前回の自分の答えも当てにならない
