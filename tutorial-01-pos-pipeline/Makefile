# tutorial-01 の操作を make で書いたもの。start.sh / stop.sh と並走している。
# どちらを使ってもよい。make のほうは入力が変わったときだけビルドし直す。
#
# 普段はリポジトリのどこからでも mk tutorial で叩く (~/.bash_aliases の mk 関数)。
# このディレクトリで直接叩いてもよい:
#
#   make up       JupyterLab を起動する  (./start.sh 相当)
#   make down     止める                 (./stop.sh 相当)
#   make reset    ノートブックを配り直す (./start.sh --reset 相当)

.DEFAULT_GOAL := help
.DELETE_ON_ERROR:                # 途中で失敗したら中途半端な生成物を消す

PORT      := 8889
NOTEBOOKS := $(wildcard notebooks/*.ipynb)
WORK_NB   := $(patsubst notebooks/%,work/%,$(NOTEBOOKS))

# docker compose build の入力。1つでも新しければイメージを作り直す。
# ビルドコンテキストがリポジトリルートなので、ルート側のファイルも入る
BUILD_DEPS := ../pyproject.toml ../uv.lock ../.python-version \
              ../drills/pyproject.toml ../quest-01-raw-ingest/pyproject.toml \
              pyproject.toml image/Dockerfile docker-compose.yml

# 複数行の文字列は define で持つ。export するとレシピから $$BANNER で読める
define BANNER

--------------------------------------------------------------------
  http://localhost:8889/lab

  work/    ノートブック (git管理外。ここに書き込む)
  /data    POSの生データ (読み取り専用)

  01-ingest.ipynb から順に開いてください。

  止めるとき      mk tutorial-down
  配り直すとき    mk tutorial-reset
--------------------------------------------------------------------
endef
export BANNER

# ---- ファイルのルール (make の本体) ---------------------------------
#
# ここに書いたものは「無ければ作る」「古ければ作り直す」で動く。
# 毎回実行される .PHONY のタスクとは性質が違う。

# 前提条件が無いので、既にあれば何もしない。
# $$ は make ではなくシェルに $ を渡すためのエスケープ
.env:
	@printf 'HOST_UID=%s\nHOST_GID=%s\n' "$$(id -u)" "$$(id -g)" > $@

work:
	@mkdir -p $@

# '|' の右は order-only 前提条件。mtime を比較せず「無ければ作る」だけになる。
# 普通の前提条件にすると、git pull で配布側の notebooks/ が新しくなった瞬間に
# work/ の自分の書き込みが消える。start.sh が
# 「既にあるファイルを上書きしない」のと同じ挙動をこれで再現している
work/%.ipynb: | notebooks/%.ipynb work
	@cp notebooks/$*.ipynb $@
	@echo "配置: $@"

# スタンプファイル。イメージそのものは make から見えないので、
# 「いつビルドしたか」を空ファイルの mtime で代用する。
# start.sh は毎回 --build を叩いていたが、こちらは入力が変わったときだけ走る
.build-stamp: $(BUILD_DEPS)
	docker compose build
	@touch $@

# ---- タスク ---------------------------------------------------------

.PHONY: help up down reset logs shell clean

help:                    ## このヘルプを出す
	@grep -hE '^[a-z][a-z-]*:.*##' $(MAKEFILE_LIST) | sed 's/:[^#]*## */\t/'

up: .env $(WORK_NB) .build-stamp   ## JupyterLab を起動する
	docker compose up -d
	@i=0; \
	while [ $$i -lt 60 ]; do \
	  curl -sf -o /dev/null http://localhost:$(PORT)/lab && break; \
	  i=$$((i + 1)); sleep 1; \
	done
	@echo "$$BANNER"

down:                    ## 止める (work/ のノートブックは残る)
	@docker compose down > /dev/null 2>&1
	@echo "止めた。(work/ のノートブックは残してある)"

reset:                   ## ノートブックを配り直す (自分の書き込みは失われる)
	rm -f $(WORK_NB)
	@$(MAKE) --no-print-directory $(WORK_NB)

logs:                    ## コンテナのログを追う
	docker compose logs -f lab

shell:                   ## コンテナに入る
	docker compose exec lab bash

clean: down              ## 生成物を消す (work/ は残す)
	rm -f .env .build-stamp
