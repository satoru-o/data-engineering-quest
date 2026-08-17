# quest-02 の操作。チュートリアルの Makefile とは違って Docker を使わない。
#
# 15分で終わる問題に、イメージのビルド待ちを付けたくなかった。
# その代わり、このクエストだけはホストに uv が要る (下の guard で確認している)。
# quest-01 のように常駐する checker も、配布用の setup.sh も無い。
#
# 普段はリポジトリのどこからでも mk quest-02 で叩く (~/.bash_aliases の mk 関数)。
# このディレクトリで直接叩いてもよい:
#
#   make check    work/solve.py を実行して判定する
#   make reset    solve.py を配り直す (自分の答えは消える)

.DEFAULT_GOAL := help
.DELETE_ON_ERROR:                # 途中で失敗したら中途半端な生成物を消す

# uv run に渡すメンバー名。workspace なので --package で教えてやる必要がある
PKG := dequest-quest02
UV  := uv run --package $(PKG) python

# ---- ファイルのルール ------------------------------------------------

work:
	@mkdir -p $@

# '|' の右は order-only 前提条件。mtime を比較せず「無ければ作る」だけになる。
# 普通の前提条件にすると、git pull で配布側の skeleton/ が新しくなった瞬間に
# work/ に書いた自分の答えが消える
work/solve.py: | skeleton/solve.py work
	@cp skeleton/solve.py $@
	@echo "配置: $@"

# ---- タスク ----------------------------------------------------------

.PHONY: help check reset clean guard

help:               ## このヘルプを出す
	@grep -hE '^[a-z][a-z0-9-]*:.*##' $(MAKEFILE_LIST) | sed 's/:[^#]*## */\t/'

# 先に古い parquet を消しておく。solve.py が途中で落ちたときに、
# 前回の出力がそのまま採点されて「直したのに結果が変わらない」となるのを防ぐ
#
# 判定の失敗は || true で飲んでいる。まだ解けていないのは正常な状態であって
# ビルドの失敗ではないので、読みやすい採点結果の下に make の Error 1 を
# 出したくない。check.py 自体は終了コードを返すので、直接叩けば分かる
check: guard work/solve.py   ## work/solve.py を実行して判定する
	@rm -f work/access_log.parquet
	@$(UV) work/solve.py
	@$(UV) check.py || true

reset:              ## solve.py を配り直す (自分の答えは消える)
	@rm -f work/solve.py
	@$(MAKE) --no-print-directory work/solve.py

clean: reset        ## 出力も消して最初の状態に戻す
	@rm -f work/access_log.parquet

# uv が無いホストで uv run と言われても意味が分からないので、先に止めて案内する
guard:
	@command -v uv >/dev/null || { \
	  echo "uv が見つかりません。このクエストだけはホストの uv を使います"; \
	  echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"; \
	  exit 1; }
