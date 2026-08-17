# quest-02 の操作。チュートリアルの Makefile とは違って Docker を使わない。
#
# 15分で終わる問題に、イメージのビルド待ちを付けたくなかった。
# その代わり、このクエストだけはホストに uv が要る (下の guard で確認している)。
# quest-01 のように常駐する checker も、配布用の setup.sh も無い。
#
# 普段はリポジトリのどこからでも mk quest-02 で叩く (~/.bash_aliases の mk 関数)。
# このディレクトリで直接叩いてもよい:
#
#   make check    採点する (問題が無ければ先に配る)
#   make new      別の3問を引き直す
#   make answer   今の3問の参考解答を出す

.DEFAULT_GOAL := help
.DELETE_ON_ERROR:                # 途中で失敗したら中途半端な生成物を消す

# uv run に渡すメンバー名。workspace なので --package で教えてやる必要がある
PKG := dequest-quest02
UV  := uv run --package $(PKG) python

STATE := work/.quest.json

# ---- ファイルのルール ------------------------------------------------

# 問題一式 (data/ と work/solve.py と .quest.json) を作る。
# 前提条件を書いていないので、既にあれば作り直さない。
# これが「解いている最中に問題が変わらない」の実体で、
# 引き直したいときだけ new が明示的に消す
$(STATE):
	@$(UV) gen.py

# ---- タスク ----------------------------------------------------------

.PHONY: help check new answer reset clean guard

help:               ## このヘルプを出す
	@grep -hE '^[a-z][a-z0-9-]*:.*##' $(MAKEFILE_LIST) | sed 's/:[^#]*## */\t/'

# 採点の失敗は || true で飲んでいる。まだ解けていないのは正常な状態であって
# ビルドの失敗ではないので、読みやすい採点結果の下に make の Error 1 を
# 出したくない。check.py 自体は終了コードを返すので、直接叩けば分かる
check: guard $(STATE)   ## 採点する (問題が無ければ先に配る)
	@$(UV) check.py || true

# gen.py を直に呼ぶ。$(STATE) のルート経由にすると、SEED の指定を間違えたときに
# 子 make の分までエラーが重なって、肝心の案内が埋もれる
new: guard          ## 別の3問を引き直す (今の答えは消える。SEED=1234 で再現できる)
	@rm -f $(STATE) work/solve.py
	@$(UV) gen.py

answer: guard       ## 今の3問の参考解答を出す
	@$(UV) answer.py || true

# 問題はそのままで solve.py だけ白紙に戻す。
# new と違って seed を引き直さないので、同じ3問をやり直せる
reset: guard        ## 今の問題のまま solve.py を白紙に戻す
	@test -f $(STATE) || { echo "問題がまだ配られていない。make new を叩くこと"; exit 1; }
	@SEED=$$($(UV) -c "import json;print(json.load(open('$(STATE)'))['seed'])") \
	  $(UV) gen.py >/dev/null
	@echo "solve.py を白紙に戻した (問題は同じ)"

clean:              ## 問題もデータも消して最初の状態に戻す
	@rm -rf work data

# uv が無いホストで uv run と言われても意味が分からないので、先に止めて案内する
guard:
	@command -v uv >/dev/null || { \
	  echo "uv が見つかりません。このクエストだけはホストの uv を使います"; \
	  echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"; \
	  exit 1; }
