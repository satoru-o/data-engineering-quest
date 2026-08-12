import marimo

__generated_with = "0.23.16"
app = marimo.App()


@app.cell(hide_code=True)
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # SQL 01. NULL・JOIN・窓関数

    DuckDB を使います。サーバも設定も要らず、CSV をそのままテーブルとして扱えます。

    集めてあるのは、**「同じつもりで書いたのに数字が変わる」ところ**です。
    原因はたいてい NULL の扱いか、JOIN で行数が変わったことのどちらかです。

    進み方はこれまでと同じで、**A と B を見比べる → 答え合わせ → ミニ練習1問**。

    これは marimo 版です。書く場所が2つあります。

    | | どこに書くか |
    | --- | --- |
    | A と B の見比べ | **SQLセル**。セル全体がそのまま SQL です |
    | ミニ練習 | Pythonセル。`q('''...''')` の中を書き換えます |

    ミニ練習だけ Python なのは、`assert` を同じセルに置く必要があるからです。
    """)
    return


@app.cell
def _():
    import duckdb
    import pandas as pd

    pd.set_option("display.width", 200)

    con = duckdb.connect()

    def q(sql):
        # SQL を実行して DataFrame で返す。ミニ練習はこれを使う
        return con.sql(sql).df()

    return con, pd, q


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    CSV から型を付けてテーブルを作ります。

    | | |
    | --- | --- |
    | `all_varchar=true` | いったん全部文字列で読む (推測させない) |
    | `nullstr` | 欠損として扱う文字列 |
    | `nullif(x, '')` | 空文字も欠損にする |

    下の3つは**SQLセル**です。`CREATE` したテーブル名は marimo が覚えるので、
    この3つを直すと下のセルが自動でやり直しになります。
    """)
    return


@app.cell
def _(con, mo):
    _t = mo.sql(
        """
        CREATE OR REPLACE TABLE orders AS
        SELECT order_id,
               nullif(customer_id, '')                        AS customer_id,
               TRY_CAST(nullif(order_date, '') AS DATE)       AS order_date,
               lower(region)                                  AS region,
               status,
               TRY_CAST(qty AS INTEGER)                       AS qty,
               TRY_CAST(replace(amount, ',', '') AS BIGINT)   AS amount
        FROM read_csv('/data/orders.csv', all_varchar=true, nullstr=['N/A', '-', 'NULL'])
        """,
        engine=con,
    )
    return


@app.cell
def _(con, mo):
    _t = mo.sql(
        """
        CREATE OR REPLACE TABLE customers AS
        SELECT customer_id, name, nullif(tier, '') AS tier,
               TRY_CAST(signup_date AS DATE) AS signup_date
        FROM read_csv('/data/customers.csv', all_varchar=true)
        """,
        engine=con,
    )
    return


@app.cell
def _(con, mo):
    _t = mo.sql(
        """
        CREATE OR REPLACE TABLE payments AS
        SELECT payment_id, order_id, TRY_CAST(paid_at AS DATE) AS paid_at,
               TRY_CAST(amount AS BIGINT) AS amount
        FROM read_csv('/data/payments.csv', all_varchar=true)
        """,
        engine=con,
    )
    return


@app.cell
def _(con, mo):
    _ab = mo.sql(
        """
        SELECT * FROM orders
        """,
        engine=con,
    )
    return


@app.cell
def _(mo, q):
    # 他の2つのテーブルも見ておく
    mo.output.append(q("SELECT * FROM customers"))
    q("SELECT * FROM payments")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    `orders.customer_id` には `C-99`(customers に無い)と欠損が1件ずつあります。
    `payments` には `O-001` に対する支払いが2件、`O-999`(orders に無い)が1件あります。
    JOIN の練習用に、わざとそうしてあります。
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 1. NULL の三値論理
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 1-1. = NULL は成立しない

    NULL は「値が無い」というより「値が不明」です。不明どうしを比べても、答えは不明です。
    """)
    return


@app.cell
def _(con, mo):
    _ab = mo.sql(
        """
        -- A: = NULL
        SELECT count(*) AS n FROM orders WHERE customer_id = NULL
        """,
        engine=con,
    )
    return


@app.cell
def _(con, mo):
    _ab = mo.sql(
        """
        -- B: IS NULL
        SELECT count(*) AS n FROM orders WHERE customer_id IS NULL
        """,
        engine=con,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <details>
    <summary>答え合わせ</summary>

    `A` は **0件**です。エラーにはなりません。

    `customer_id = NULL` は `TRUE` でも `FALSE` でもなく **`NULL`(不明)** を返します。
    `WHERE` は `TRUE` の行だけを通すので、1行も通りません。

    これが SQL の**三値論理**です。`TRUE` / `FALSE` / `NULL` の3つがあります。

    | 式 | 結果 |
    | --- | --- |
    | `NULL = NULL` | `NULL` |
    | `NULL <> NULL` | `NULL` |
    | `NULL IS NULL` | `TRUE` |

    判定には `IS NULL` / `IS NOT NULL` を使います。

    </details>
    """)
    return


@app.cell
def _(mo, q):
    # ミニ練習: order_date が NULL の注文の件数を出す

    _ans = q('''
        SELECT 1 AS dummy   -- ここを書き換える
    ''')

    mo.output.append(_ans)
    assert _ans["n"].iloc[0] == 1, _ans.to_dict()
    print("OK")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <details>
    <summary>答え</summary>

    ```python
    _ans = q('''
    SELECT count(*) AS n FROM orders WHERE order_date IS NULL
    ''')
    ```

    </details>
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 1-2. NOT IN と NULL

    サブクエリに NULL が1つでも入ると、`NOT IN` は何も返さなくなります。
    """)
    return


@app.cell
def _(con, mo):
    _ab = mo.sql(
        """
        -- A: NOT IN
        SELECT count(*) AS n
        FROM customers
        WHERE customer_id NOT IN (SELECT customer_id FROM orders)
        """,
        engine=con,
    )
    return


@app.cell
def _(con, mo):
    _ab = mo.sql(
        """
        -- B: NOT EXISTS
        SELECT count(*) AS n
        FROM customers c
        WHERE NOT EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.customer_id)
        """,
        engine=con,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <details>
    <summary>答え合わせ</summary>

    `A` は **0件**、`B` は **1件**(注文の無い `C-05`)。正しいのは `B` です。

    `orders.customer_id` には NULL が1件あります。すると

    ```
    'C-05' NOT IN ('C-01', ..., NULL)
      = 'C-05' <> 'C-01' AND ... AND 'C-05' <> NULL
      = TRUE AND ... AND NULL
      = NULL          ← TRUE にならないので通らない
    ```

    **サブクエリに NULL が1つでもあれば、`NOT IN` は必ず0件になります。**
    エラーも警告も出ません。

    対策は3つあります。

    - `NOT EXISTS` を使う(いちばん素直)
    - `LEFT JOIN ... WHERE 右.key IS NULL`(anti join。2-4 でやります)
    - サブクエリ側に `WHERE key IS NOT NULL` を付ける

    </details>
    """)
    return


@app.cell
def _(mo, q):
    # ミニ練習: orders に存在しない order_id を持つ payments を出す (NOT EXISTS で)

    _ans = q('''
        SELECT 1 AS dummy   -- ここを書き換える
    ''')

    mo.output.append(_ans)
    assert _ans["payment_id"].tolist() == ["P-05"], _ans["payment_id"].tolist()
    print("OK")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <details>
    <summary>答え</summary>

    ```python
    _ans = q('''
    SELECT payment_id
    FROM payments p
    WHERE NOT EXISTS (SELECT 1 FROM orders o WHERE o.order_id = p.order_id)
    ''')
    ```

    </details>
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 1-3. COUNT(*) と COUNT(col)

    件数の数え方です。pandas の `size` と `count` に対応します。
    """)
    return


@app.cell
def _(con, mo):
    _ab = mo.sql(
        """
        -- A: 並べて見る
        SELECT count(*)                 AS c_star,
               count(amount)            AS c_amount,
               count(DISTINCT region)   AS c_region,
               sum(amount)              AS total,
               avg(amount)              AS average
        FROM orders
        """,
        engine=con,
    )
    return


@app.cell
def _(con, mo):
    _ab = mo.sql(
        """
        -- B: 平均を自分で計算してみる
        SELECT sum(amount) AS total,
               count(amount) AS n_not_null,
               count(*) AS n_all,
               sum(amount) / count(amount) AS avg_by_notnull,
               sum(amount) / count(*)      AS avg_by_all
        FROM orders
        """,
        engine=con,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <details>
    <summary>答え合わせ</summary>

    - `count(*)` は**行数**。12
    - `count(amount)` は**NULL でない数**。11
    - `count(DISTINCT col)` は種類数。NULL は数えません

    **`avg` の分母は `count(col)`、つまり NULL を除いた数**です。
    `sum / count(*)` とは一致しません。「平均が思ったより高い」の原因はたいていこれです。

    `sum` も NULL を無視します。ついでに、**全部 NULL のときの `sum` は 0 ではなく NULL** です。
    0 にしておきたいときは `coalesce(sum(amount), 0)` とします。

    </details>
    """)
    return


@app.cell
def _(mo, q):
    # ミニ練習: 行数 n_all と、qty が入っている行数 n_qty を並べて出す

    _ans = q('''
        SELECT 1 AS dummy   -- ここを書き換える
    ''')

    mo.output.append(_ans)
    assert _ans["n_all"].iloc[0] == 12
    assert _ans["n_qty"].iloc[0] == 11, _ans.to_dict()
    print("OK")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <details>
    <summary>答え</summary>

    ```python
    _ans = q('''
    SELECT count(*) AS n_all, count(qty) AS n_qty FROM orders
    ''')
    ```

    </details>
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 1-4. GROUP BY と NULL

    キーが NULL の行はどうなるか。**pandas とは動きが違います。**
    """)
    return


@app.cell
def _(con, mo):
    _ab = mo.sql(
        """
        -- A: SQL
        SELECT customer_id, count(*) AS n, sum(amount) AS total
        FROM orders
        GROUP BY customer_id
        ORDER BY customer_id
        """,
        engine=con,
    )
    return


@app.cell
def _(q):
    # B: pandas (既定)
    _o = q("SELECT * FROM orders")
    _o.groupby("customer_id", as_index=False, dropna=True).agg(
        n=("order_id", "size"), total=("amount", "sum"))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <details>
    <summary>答え合わせ</summary>

    **SQL は NULL も1つのグループとして残します。pandas は既定で捨てます。**

    | | キーが NULL の行 |
    | --- | --- |
    | SQL `GROUP BY` | 1グループとして残る |
    | pandas `groupby` | **既定で消える**(`dropna=True`) |

    SQL のクエリを pandas に書き直すと、ここで合計が変わります。
    pandas 側で `dropna=False` を付けると揃います。

    </details>
    """)
    return


@app.cell
def _(mo, q):
    # ミニ練習: status ごとの件数を出す (status, n の2列。status 昇順)

    _ans = q('''
        SELECT 1 AS dummy   -- ここを書き換える
    ''')

    mo.output.append(_ans)
    assert _ans["status"].tolist() == ["cancelled", "completed", "pending"]
    assert _ans["n"].tolist() == [1, 9, 2], _ans["n"].tolist()
    print("OK")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <details>
    <summary>答え</summary>

    ```python
    _ans = q('''
    SELECT status, count(*) AS n
    FROM orders
    GROUP BY status
    ORDER BY status
    ''')
    ```

    </details>
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 2. JOIN
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 2-1. INNER と LEFT

    結合できなかった行をどうするか、の違いです。行数を必ず見ます。
    """)
    return


@app.cell
def _(con, mo):
    _ab = mo.sql(
        """
        -- A: INNER JOIN
        SELECT o.order_id, o.customer_id, c.name, c.tier
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        ORDER BY o.order_id
        """,
        engine=con,
    )
    return


@app.cell
def _(con, mo):
    _ab = mo.sql(
        """
        -- B: LEFT JOIN
        SELECT o.order_id, o.customer_id, c.name, c.tier
        FROM orders o
        LEFT JOIN customers c ON o.customer_id = c.customer_id
        ORDER BY o.order_id
        """,
        engine=con,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <details>
    <summary>答え合わせ</summary>

    `A` は **10行**、`B` は **12行**です。

    `INNER` は両方にある行だけを残すので、`O-009`(顧客 `C-99` が customers に無い)と
    `O-010`(customer_id が NULL)が**黙って消えます**。

    `B` の LEFT JOIN なら全部残り、右側が `None` になります。

    「JOIN したら件数が減った」は、仕様どおりの動きです。ただし気づかないと事故になるので、
    JOIN の前後で行数を比べる習慣をつけておくと安心です。

    なお `ON` の等値比較でも NULL は一致しないので、
    `customer_id` が NULL の行は LEFT JOIN でも右側が埋まりません。

    </details>
    """)
    return


@app.cell
def _(mo, q):
    # ミニ練習: 注文を全部残したまま顧客名を付ける (order_id, name の2列。order_id 昇順)

    _ans = q('''
        SELECT 1 AS dummy   -- ここを書き換える
    ''')

    mo.output.append(_ans)
    assert len(_ans) == 12, f"12行のはず: {len(_ans)}"
    assert _ans["name"].isna().sum() == 2, "結合できない行が消えている"
    print("OK")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <details>
    <summary>答え</summary>

    ```python
    _ans = q('''
    SELECT o.order_id, c.name
    FROM orders o
    LEFT JOIN customers c ON o.customer_id = c.customer_id
    ORDER BY o.order_id
    ''')
    ```

    </details>
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 2-2. LEFT JOIN の ON と WHERE

    条件を `ON` に書くか `WHERE` に書くかで、**結果が変わります**。
    """)
    return


@app.cell
def _(con, mo):
    _ab = mo.sql(
        """
        -- A: ON に書く
        SELECT o.order_id, c.name, c.tier
        FROM orders o
        LEFT JOIN customers c
          ON o.customer_id = c.customer_id AND c.tier = 'gold'
        ORDER BY o.order_id
        """,
        engine=con,
    )
    return


@app.cell
def _(con, mo):
    _ab = mo.sql(
        """
        -- B: WHERE に書く
        SELECT o.order_id, c.name, c.tier
        FROM orders o
        LEFT JOIN customers c
          ON o.customer_id = c.customer_id
        WHERE c.tier = 'gold'
        ORDER BY o.order_id
        """,
        engine=con,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <details>
    <summary>答え合わせ</summary>

    `A` は **12行**(全注文。gold でなければ右が NULL)。`B` は **6行**です。

    処理の順番はこうなっています。

    ```
    1. ON の条件で結合する       (LEFT なので左は全部残る)
    2. WHERE で絞る             ← ここで右が NULL の行も落ちる
    ```

    `WHERE c.tier = 'gold'` は、右が NULL の行に対して `NULL = 'gold'` → `NULL` を返すので、
    その行が落ちます。結果として **LEFT JOIN が INNER JOIN のようになってしまいます**。

    覚え方はシンプルです。

    - **右側を絞る条件は `ON` に書く**
    - **左側を絞る条件は `WHERE` に書く**

    </details>
    """)
    return


@app.cell
def _(mo, q):
    # ミニ練習: 全注文を残したまま、silver の顧客だけ名前を付ける
    #           (order_id, name の2列。条件は ON に書く)

    _ans = q('''
        SELECT 1 AS dummy   -- ここを書き換える
    ''')

    mo.output.append(_ans)
    assert len(_ans) == 12, f"12行のはず (WHERE に書くと減る): {len(_ans)}"
    assert _ans["name"].notna().sum() == 3, _ans["name"].tolist()
    print("OK")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <details>
    <summary>答え</summary>

    ```python
    _ans = q('''
    SELECT o.order_id, c.name
    FROM orders o
    LEFT JOIN customers c
      ON o.customer_id = c.customer_id AND c.tier = 'silver'
    ORDER BY o.order_id
    ''')
    ```

    </details>
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 2-3. 1対多で行が増える

    JOIN で行数が増えると、集計が壊れます。
    """)
    return


@app.cell
def _(con, mo):
    _ab = mo.sql(
        """
        -- A: そのまま JOIN
        SELECT o.order_id, o.amount, p.payment_id, p.amount AS paid
        FROM orders o
        JOIN payments p ON o.order_id = p.order_id
        ORDER BY o.order_id
        """,
        engine=con,
    )
    return


@app.cell
def _(con, mo):
    _ab = mo.sql(
        """
        -- B: 先に集計してから JOIN
        SELECT o.order_id, o.amount, p.n_payments, p.paid
        FROM orders o
        LEFT JOIN (
          SELECT order_id, count(*) AS n_payments, sum(amount) AS paid
          FROM payments GROUP BY order_id
        ) p ON o.order_id = p.order_id
        ORDER BY o.order_id
        """,
        engine=con,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <details>
    <summary>答え合わせ</summary>

    `O-001` には支払いが2件あるので、`A` では `O-001` の行が**2行に増えます**。
    この状態で `sum(o.amount)` すると、注文金額が二重に足されます。

    これは「JOIN による水増し(fan-out)」と呼ばれ、集計が合わない原因の筆頭です。

    対策は `B` です。**多いほうを先に集約して1対1にしてから JOIN します。**

    JOIN を書いたら「この結合は1対1か、1対多か」を一度考える、
    これだけでかなり防げます。

    </details>
    """)
    return


@app.cell
def _(mo, q):
    # ミニ練習: order_id ごとの支払い件数と合計を出す (order_id, n_payments, paid)

    _ans = q('''
        SELECT 1 AS dummy   -- ここを書き換える
    ''')

    mo.output.append(_ans)
    assert len(_ans) == 4, f"4行のはず: {len(_ans)}"
    assert _ans.set_index("order_id").loc["O-001", "n_payments"] == 2
    print("OK")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <details>
    <summary>答え</summary>

    ```python
    _ans = q('''
    SELECT order_id, count(*) AS n_payments, sum(amount) AS paid
    FROM payments
    GROUP BY order_id
    ORDER BY order_id
    ''')
    ```

    </details>
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 2-4. ANTI JOIN — 片方にしか無いもの

    「注文の無い顧客」を出す2つの書き方です。
    """)
    return


@app.cell
def _(con, mo):
    _ab = mo.sql(
        """
        -- A: LEFT JOIN + IS NULL
        SELECT c.customer_id, c.name
        FROM customers c
        LEFT JOIN orders o ON c.customer_id = o.customer_id
        WHERE o.order_id IS NULL
        """,
        engine=con,
    )
    return


@app.cell
def _(con, mo):
    _ab = mo.sql(
        """
        -- B: ANTI JOIN (DuckDB の構文)
        SELECT c.customer_id, c.name
        FROM customers c
        ANTI JOIN orders o ON c.customer_id = o.customer_id
        """,
        engine=con,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <details>
    <summary>答え合わせ</summary>

    どちらも `C-05` の1件です。

    `A` はどのデータベースでも動きます。`B` は DuckDB などが持つ専用構文で、意図が明確です。

    `A` を書くときは **`WHERE 右.列 IS NULL`** に何の列を指定するかに注意します。
    もともと NULL がありうる列を指定すると、結合できているのに拾ってしまいます。
    主キーを指定しておくのが安全です。

    </details>
    """)
    return


@app.cell
def _(mo, q):
    # ミニ練習: LEFT JOIN + IS NULL で「支払いが1件も無い注文」の件数を出す

    _ans = q('''
        SELECT 1 AS dummy   -- ここを書き換える
    ''')

    mo.output.append(_ans)
    assert _ans["n"].iloc[0] == 9, _ans.to_dict()
    print("OK")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <details>
    <summary>答え</summary>

    ```python
    _ans = q('''
    SELECT count(*) AS n
    FROM orders o
    LEFT JOIN payments p ON o.order_id = p.order_id
    WHERE p.payment_id IS NULL
    ''')
    ```

    </details>
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 3. WHERE と HAVING
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 3-1. 絞る位置

    集約の前に絞るか、後に絞るかの違いです。
    """)
    return


@app.cell
def _(con, mo):
    _ab = mo.sql(
        """
        -- A: WHERE (集約の前)
        SELECT region, count(*) AS n, sum(amount) AS total
        FROM orders
        WHERE status = 'completed'
        GROUP BY region
        ORDER BY region
        """,
        engine=con,
    )
    return


@app.cell
def _(con, mo):
    _ab = mo.sql(
        """
        -- B: HAVING (集約の後)
        SELECT region, count(*) AS n, sum(amount) AS total
        FROM orders
        GROUP BY region
        HAVING sum(amount) > 5000
        ORDER BY region
        """,
        engine=con,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <details>
    <summary>答え合わせ</summary>

    SQL の処理はこの順に進みます。

    ```
    FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY → LIMIT
    ```

    - `WHERE` は**行**を絞ります。集約の前なので、集約結果に影響します
    - `HAVING` は**グループ**を絞ります。集約の後なので `sum()` を条件に使えます

    `WHERE sum(amount) > 5000` とは書けません(その時点ではまだ集約していないため)。

    どちらでも書けるときは `WHERE` に書きます。先に行を減らすほうが速いからです。

    `SELECT` が `GROUP BY` より後なので、`SELECT` で付けた別名は `WHERE` では使えません。
    `ORDER BY` では使えます(そちらは後ろだから)。

    </details>
    """)
    return


@app.cell
def _(mo, q):
    # ミニ練習: 注文が4件以上ある region だけを出す (region, n。region 昇順)

    _ans = q('''
        SELECT 1 AS dummy   -- ここを書き換える
    ''')

    mo.output.append(_ans)
    assert _ans["region"].tolist() == ["east", "west"], _ans["region"].tolist()
    print("OK")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <details>
    <summary>答え</summary>

    ```python
    _ans = q('''
    SELECT region, count(*) AS n
    FROM orders
    GROUP BY region
    HAVING count(*) >= 4
    ORDER BY region
    ''')
    ```

    </details>
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 4. 窓関数

    **「キーごとに最新の1行」を SQL で書きます。**
    pandas の `drop_duplicates(keep="last")` に当たる処理です。

    まず、`pandas-03` と同じ形のデータを作ります。
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    訂正が後から届いた状況を、その場で組み立てます。
    """)
    return


@app.cell
def _(con, mo):
    _t = mo.sql(
        """
        CREATE OR REPLACE TABLE raw AS
        SELECT * FROM (VALUES
          ('O-002', TIMESTAMP '2024-02-01 09:00', 980,  'pending'),
          ('O-001', TIMESTAMP '2024-02-01 10:00', 2400, 'completed'),
          ('O-001', TIMESTAMP '2024-02-02 10:00', NULL, 'cancelled'),
          ('O-003', TIMESTAMP '2024-02-01 11:00', 3600, 'completed')
        ) AS t(order_id, ingested_at, amount, status)
        """,
        engine=con,
    )
    return


@app.cell
def _(con, mo):
    _ab = mo.sql(
        """
        SELECT * FROM raw ORDER BY order_id, ingested_at
        """,
        engine=con,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 4-1. row_number で1行選ぶ

    窓関数のいちばん定番の使い方です。
    """)
    return


@app.cell
def _(con, mo):
    _ab = mo.sql(
        """
        -- A: まず番号を振ってみる
        SELECT *,
               row_number() OVER (PARTITION BY order_id ORDER BY ingested_at DESC) AS rn
        FROM raw
        ORDER BY order_id, rn
        """,
        engine=con,
    )
    return


@app.cell
def _(con, mo):
    _ab = mo.sql(
        """
        -- B: 1番だけ残す
        SELECT order_id, ingested_at, amount, status
        FROM (
          SELECT *, row_number() OVER (PARTITION BY order_id ORDER BY ingested_at DESC) AS rn
          FROM raw
        ) WHERE rn = 1
        ORDER BY order_id
        """,
        engine=con,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <details>
    <summary>答え合わせ</summary>

    `OVER (PARTITION BY ... ORDER BY ...)` は「グループごとに並べて番号を振る」という意味です。
    `GROUP BY` と違って**行が減らない**のがポイントで、番号を振ってから `WHERE rn = 1` で絞ります。

    `O-001` の `amount` は **NULL のまま**です。pandas の `groupby().last()` のように
    別の行から値を拾ってくることはありません。**SQL の窓関数は必ず行を選びます。**

    `WHERE rn = 1` を同じ階層に書けないのは、`SELECT` より `WHERE` が先に評価されるためです
    (3-1 の実行順)。サブクエリか CTE で1段包みます。

    </details>
    """)
    return


@app.cell
def _(mo, q):
    # ミニ練習: 同じ形で「order_id ごとに いちばん古い1行」を出す (order_id 昇順)

    _ans = q('''
        SELECT 1 AS dummy   -- ここを書き換える
    ''')

    mo.output.append(_ans)
    assert len(_ans) == 3
    assert _ans["amount"].tolist() == [2400, 980, 3600], _ans["amount"].tolist()
    print("OK")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <details>
    <summary>答え</summary>

    ```python
    _ans = q('''
    SELECT order_id, ingested_at, amount, status
    FROM (
      SELECT *, row_number() OVER (PARTITION BY order_id ORDER BY ingested_at) AS rn
      FROM raw
    ) WHERE rn = 1
    ORDER BY order_id
    ''')
    ```

    </details>
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 4-2. QUALIFY で1段減らす

    DuckDB / Snowflake / BigQuery にある構文で、窓関数の結果を直接絞れます。
    """)
    return


@app.cell
def _(con, mo):
    _ab = mo.sql(
        """
        -- A: サブクエリ
        SELECT order_id, amount, status FROM (
          SELECT *, row_number() OVER (PARTITION BY order_id ORDER BY ingested_at DESC) AS rn
          FROM raw
        ) WHERE rn = 1 ORDER BY order_id
        """,
        engine=con,
    )
    return


@app.cell
def _(con, mo):
    _ab = mo.sql(
        """
        -- B: QUALIFY
        SELECT order_id, amount, status
        FROM raw
        QUALIFY row_number() OVER (PARTITION BY order_id ORDER BY ingested_at DESC) = 1
        ORDER BY order_id
        """,
        engine=con,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <details>
    <summary>答え合わせ</summary>

    同じ結果です。`QUALIFY` は「窓関数に対する HAVING」だと思ってください。

    ```
    WHERE   … 行を絞る    (集約の前)
    HAVING  … 群を絞る    (集約の後)
    QUALIFY … 窓関数の結果で絞る
    ```

    PostgreSQL や MySQL には無いので、移植性が要るなら `A` の書き方にします。

    </details>
    """)
    return


@app.cell
def _(mo, pd, q):
    # ミニ練習: QUALIFY を使って「order_id ごとに最新の1行」を出す (order_id 昇順)

    _ans = q('''
        SELECT 1 AS dummy   -- ここを書き換える
    ''')

    mo.output.append(_ans)
    assert len(_ans) == 3
    assert pd.isna(_ans["amount"].iloc[0]), "O-001 の amount は NULL のまま"
    print("OK")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <details>
    <summary>答え</summary>

    ```python
    _ans = q('''
    SELECT order_id, amount, status
    FROM raw
    QUALIFY row_number() OVER (PARTITION BY order_id ORDER BY ingested_at DESC) = 1
    ORDER BY order_id
    ''')
    ```

    </details>
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 4-3. row_number / rank / dense_rank

    同じ値が並んだときの扱いです。pandas の `rank(method=)` に対応します。
    """)
    return


@app.cell
def _(con, mo):
    _ab = mo.sql(
        """
        -- A: east の注文に3つ並べてみる
        SELECT region, amount,
               row_number() OVER (PARTITION BY region ORDER BY amount DESC) AS rn,
               rank()       OVER (PARTITION BY region ORDER BY amount DESC) AS rk,
               dense_rank() OVER (PARTITION BY region ORDER BY amount DESC) AS drk
        FROM orders
        WHERE region = 'east'
        ORDER BY amount DESC NULLS LAST
        """,
        engine=con,
    )
    return


@app.cell
def _(con, mo):
    _ab = mo.sql(
        """
        -- B: 同じ値があるデータで
        SELECT x,
               row_number() OVER (ORDER BY x) AS rn,
               rank()       OVER (ORDER BY x) AS rk,
               dense_rank() OVER (ORDER BY x) AS drk
        FROM (VALUES (10), (20), (20), (30)) AS t(x)
        ORDER BY x
        """,
        engine=con,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <details>
    <summary>答え合わせ</summary>

    | 関数 | 10, 20, 20, 30 に対して | pandas |
    | --- | --- | --- |
    | `row_number()` | 1, 2, 3, 4 | `rank(method="first")` |
    | `rank()` | 1, 2, 2, **4** | `rank(method="min")` |
    | `dense_rank()` | 1, 2, 2, **3** | `rank(method="dense")` |

    **`row_number()` は同じ順位を作りません。** なので「1行だけ選ぶ」用途では
    `rank()` ではなく `row_number()` を使います(`rank()` だと同着で2行返ります)。

    ただし `ORDER BY` が同着だと、`row_number()` がどちらを1にするかは決まりません。
    pandas と同じで、**2つめのキーを足して並び順を一意に**しておきます。

    </details>
    """)
    return


@app.cell
def _(mo, q):
    # ミニ練習: region ごとに amount の大きい順で番号 rn を振る (region, order_id, rn)
    #           amount が NULL の行があってもよい

    _ans = q('''
        SELECT 1 AS dummy   -- ここを書き換える
    ''')

    mo.output.append(_ans)
    assert set(_ans.columns) == {"region", "order_id", "rn"}, list(_ans.columns)
    assert len(_ans) == 12
    assert (_ans["rn"] == 1).sum() == 4, "region ごとに1が1つずつのはず"
    print("OK")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <details>
    <summary>答え</summary>

    ```python
    _ans = q('''
    SELECT region, order_id,
           row_number() OVER (PARTITION BY region ORDER BY amount DESC) AS rn
    FROM orders
    ORDER BY region, rn
    ''')
    ```

    </details>
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 4-4. ORDER BY と NULL の位置

    並べ替えたとき、NULL がどこに行くかはデータベースによって違います。
    """)
    return


@app.cell
def _(con, mo):
    _ab = mo.sql(
        """
        -- A: 既定
        SELECT order_id, amount FROM orders
        ORDER BY amount DESC
        LIMIT 4
        """,
        engine=con,
    )
    return


@app.cell
def _(con, mo):
    _ab = mo.sql(
        """
        -- B: 明示する
        SELECT order_id, amount FROM orders
        ORDER BY amount DESC NULLS LAST
        LIMIT 4
        """,
        engine=con,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <details>
    <summary>答え合わせ</summary>

    DuckDB と PostgreSQL の既定は「`ASC` なら NULL は最後、`DESC` なら最初」です。
    MySQL は逆です。

    `NULLS FIRST` / `NULLS LAST` を書いておけば、どこでも同じ結果になります。

    `ORDER BY amount DESC LIMIT 1` で「最大の行」を取るつもりのクエリは、
    NULL が先に来るデータベースでは **NULL の行が取れてしまいます**。

    </details>
    """)
    return


@app.cell
def _(mo, q):
    # ミニ練習: amount の昇順で、NULL を先頭に並べたときの1件目を出す

    _ans = q('''
        SELECT 1 AS dummy   -- ここを書き換える
    ''')

    mo.output.append(_ans)
    assert _ans["order_id"].iloc[0] == "O-006", _ans.to_dict()
    print("OK")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <details>
    <summary>答え</summary>

    ```python
    _ans = q('''
    SELECT order_id, amount FROM orders
    ORDER BY amount ASC NULLS FIRST
    LIMIT 1
    ''')
    ```

    </details>
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 仕上げ

    ここまでの組み合わせです。答えを見ながらでも大丈夫です。
    """)
    return


@app.cell
def _(mo, q):
    # 仕上げ1: 顧客ごとに、注文件数と金額合計を出す。
    #          customers に載っていない顧客 (C-99) と、customer_id が欠損の注文も
    #          1行として残すこと。列は customer_id, name, n_orders, total。
    #          name は customers に無ければ NULL のままでよい。

    _ans = q('''
        SELECT 1 AS dummy   -- ここを書き換える
    ''')

    mo.output.append(_ans)
    assert len(_ans) == 6, f"6行のはず: {len(_ans)}"
    assert _ans["n_orders"].sum() == 12, f"注文が全部数えられていない: {_ans['n_orders'].sum()}"
    assert _ans["total"].sum() == 23220
    print("OK")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <details>
    <summary>答え</summary>

    ```python
    _ans = q('''
    SELECT o.customer_id, c.name,
           count(*) AS n_orders,
           sum(o.amount) AS total
    FROM orders o
    LEFT JOIN customers c ON o.customer_id = c.customer_id
    GROUP BY o.customer_id, c.name
    ORDER BY o.customer_id
    ''')
    ```

    </details>
    """)
    return


@app.cell
def _(mo, q):
    # 仕上げ2: 支払いが1件も無い注文の order_id を出す。order_id 昇順。

    _ans = q('''
        SELECT 1 AS dummy   -- ここを書き換える
    ''')

    mo.output.append(_ans)
    assert _ans["order_id"].tolist() == ["O-002", "O-004", "O-006", "O-007",
                                        "O-008", "O-009", "O-010", "O-011",
                                        "O-012"], _ans["order_id"].tolist()
    print("OK")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <details>
    <summary>答え</summary>

    ```python
    _ans = q('''
    SELECT o.order_id
    FROM orders o
    WHERE NOT EXISTS (SELECT 1 FROM payments p WHERE p.order_id = o.order_id)
    ORDER BY o.order_id
    ''')
    ```

    </details>
    """)
    return


@app.cell
def _(mo, q):
    # 仕上げ3: 地域ごとに金額が最も大きい注文を1件ずつ出す。
    #          列は region, order_id, amount。region 昇順。
    #          (同額のときは order_id の小さいほうを選ぶ)

    _ans = q('''
        SELECT 1 AS dummy   -- ここを書き換える
    ''')

    mo.output.append(_ans)
    assert len(_ans) == 4, f"4行のはず: {len(_ans)}"
    assert _ans["region"].tolist() == ["east", "north", "south", "west"]
    assert _ans["order_id"].tolist() == ["O-009", "O-005", "O-007", "O-004"], _ans["order_id"].tolist()
    print("OK")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <details>
    <summary>答え</summary>

    ```python
    _ans = q('''
    SELECT region, order_id, amount
    FROM orders
    QUALIFY row_number() OVER (
      PARTITION BY region ORDER BY amount DESC NULLS LAST, order_id
    ) = 1
    ORDER BY region
    ''')
    ```

    </details>
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## まとめ

    ### NULL

    | 書き方 | 意味 |
    | --- | --- |
    | `= NULL` | **常に NULL。0件になる** |
    | `IS NULL` / `IS NOT NULL` | 正しい判定 |
    | `NOT IN (サブクエリ)` | **NULL が1つでもあれば0件** |
    | `NOT EXISTS` | 安全。第一候補 |
    | `count(*)` / `count(col)` | 行数 / 非NULL数 |
    | `avg(col)` | 分母は `count(col)`。NULL を除く |
    | `sum(col)` | 全部 NULL なら 0 ではなく **NULL** |
    | `GROUP BY` | NULL を1グループとして残す(pandas と逆) |

    ### JOIN

    | | 意味 |
    | --- | --- |
    | `INNER` | 両方にある行だけ。**黙って減る** |
    | `LEFT` | 左を全部残す |
    | `ANTI` / `LEFT + IS NULL` | 片方にしか無いもの |
    | 条件を `ON` に書く | 右側を絞る |
    | 条件を `WHERE` に書く | **LEFT JOIN が INNER のようになる** |
    | 1対多 | **行が増えて二重計上**。先に集約する |

    ### 窓関数

    | | |
    | --- | --- |
    | `OVER (PARTITION BY ... ORDER BY ...)` | 行を減らさずにグループ内で計算 |
    | `row_number()` | 同じ順位を作らない。**1行選ぶならこれ** |
    | `rank()` / `dense_rank()` | 同順位あり。次を飛ばす / 飛ばさない |
    | `QUALIFY` | 窓関数の結果で絞る (DuckDB/Snowflake/BigQuery) |
    | `NULLS FIRST` / `NULLS LAST` | **DBによって既定が違う。明示する** |

    ### 実行順

    ```
    FROM → WHERE → GROUP BY → HAVING → 窓関数 → QUALIFY → SELECT → ORDER BY → LIMIT
    ```

    `SELECT` の別名が `WHERE` で使えず `ORDER BY` で使えるのは、この順番のためです。
    """)
    return


if __name__ == "__main__":
    app.run()
