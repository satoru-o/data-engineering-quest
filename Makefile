# リポジトリ全体の入口。中身は各ディレクトリの Makefile に投げるだけ。
#
# make 化されているのは今のところチュートリアルだけ。
# drills / quest-01 は従来どおり cd して ./start.sh / ./setup.sh を叩く。
#
# ~/.bash_aliases に mk 関数を入れてあるので、リポジトリ内のどの階層からでも
#
#   mk tutorial-01        POS売上パイプラインを起動する
#   mk tutorial-02        社員名簿クレンジングを起動する
#   mk tutorial-01-down   止める
#   mk <TAB>              ターゲット候補を出す
#
# で叩ける。make には git のような「上の階層を探しに行く」機能が無いので、
# mk 側が git rev-parse --show-toplevel でルートを見つけて -C で渡している。

.DEFAULT_GOAL := help

TUTORIAL01 := tutorial-01-pos-pipeline
TUTORIAL02 := tutorial-02-roster-cleaning

# 子の make を呼ぶ。レシピ側は必ず頭に + を付けること。
#
# make が「この行は再帰呼び出しだ」と判断するのは、展開する前のレシピ文字列に
# $(MAKE) という字面があるかどうかで見ている。ここのように変数越しに書くと
# 字面が出てこないので検出されず、-n で子まで降りなくなり、-j のときも
# jobserver が渡らない。行頭の + はそれを明示的に伝える印
SUB = $(MAKE) --no-print-directory -C

.PHONY: help \
        tutorial-01 tutorial-01-down tutorial-01-reset tutorial-01-logs tutorial-01-shell \
        tutorial-02 tutorial-02-down tutorial-02-reset tutorial-02-logs tutorial-02-shell \
        tutorial tutorial-down tutorial-reset tutorial-logs tutorial-shell

help:               ## このヘルプを出す
	@grep -hE '^[a-z][a-z0-9-]*:.*##' $(MAKEFILE_LIST) | sed 's/:[^#]*## */\t/'

tutorial-01:        ## tutorial-01 POS売上パイプライン を起動する (http://localhost:8889/lab)
	@+$(SUB) $(TUTORIAL01) up

tutorial-01-down:   ## tutorial-01 を止める
	@+$(SUB) $(TUTORIAL01) down

tutorial-01-reset:  ## tutorial-01 のノートブックを配り直す (自分の書き込みは失われる)
	@+$(SUB) $(TUTORIAL01) reset

tutorial-01-logs:   ## tutorial-01 のログを追う
	@+$(SUB) $(TUTORIAL01) logs

tutorial-01-shell:  ## tutorial-01 のコンテナに入る
	@+$(SUB) $(TUTORIAL01) shell

tutorial-02:        ## tutorial-02 社員名簿クレンジング を起動する (http://localhost:8890/lab)
	@+$(SUB) $(TUTORIAL02) up

tutorial-02-down:   ## tutorial-02 を止める
	@+$(SUB) $(TUTORIAL02) down

tutorial-02-reset:  ## tutorial-02 のノートブックを配り直す (自分の書き込みは失われる)
	@+$(SUB) $(TUTORIAL02) reset

tutorial-02-logs:   ## tutorial-02 のログを追う
	@+$(SUB) $(TUTORIAL02) logs

tutorial-02-shell:  ## tutorial-02 のコンテナに入る
	@+$(SUB) $(TUTORIAL02) shell

# チュートリアルが1本だけだった頃の名前。手癖で叩けるように残してある。
# ## を付けていないので help には出ない (help は ## のある行だけを拾う)
tutorial:        ; @+$(SUB) $(TUTORIAL01) up
tutorial-down:   ; @+$(SUB) $(TUTORIAL01) down
tutorial-reset:  ; @+$(SUB) $(TUTORIAL01) reset
tutorial-logs:   ; @+$(SUB) $(TUTORIAL01) logs
tutorial-shell:  ; @+$(SUB) $(TUTORIAL01) shell
