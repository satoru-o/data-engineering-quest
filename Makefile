# リポジトリ全体の入口。中身は各ディレクトリの Makefile に投げるだけ。
#
# make 化されているのは今のところ tutorial-01 だけ (パイロット中)。
# drills / quest-01 は従来どおり cd して ./start.sh / ./setup.sh を叩く。
#
# ~/.bash_aliases に mk 関数を入れてあるので、リポジトリ内のどの階層からでも
#
#   mk tutorial        起動する
#   mk tutorial-down   止める
#   mk <TAB>           ターゲット候補を出す
#
# で叩ける。make には git のような「上の階層を探しに行く」機能が無いので、
# mk 側が git rev-parse --show-toplevel でルートを見つけて -C で渡している。

.DEFAULT_GOAL := help

TUTORIAL := tutorial-01-pos-pipeline

# 子の make を呼ぶ。レシピ側は必ず頭に + を付けること。
#
# make が「この行は再帰呼び出しだ」と判断するのは、展開する前のレシピ文字列に
# $(MAKE) という字面があるかどうかで見ている。ここのように変数越しに書くと
# 字面が出てこないので検出されず、-n で子まで降りなくなり、-j のときも
# jobserver が渡らない。行頭の + はそれを明示的に伝える印
SUB = $(MAKE) --no-print-directory -C

.PHONY: help tutorial tutorial-down tutorial-reset tutorial-logs tutorial-shell

help:               ## このヘルプを出す
	@grep -hE '^[a-z][a-z-]*:.*##' $(MAKEFILE_LIST) | sed 's/:[^#]*## */\t/'

tutorial:           ## JupyterLab を起動する (http://localhost:8889/lab)
	@+$(SUB) $(TUTORIAL) up

tutorial-down:      ## 止める
	@+$(SUB) $(TUTORIAL) down

tutorial-reset:     ## ノートブックを配り直す (自分の書き込みは失われる)
	@+$(SUB) $(TUTORIAL) reset

tutorial-logs:      ## ログを追う
	@+$(SUB) $(TUTORIAL) logs

tutorial-shell:     ## コンテナに入る
	@+$(SUB) $(TUTORIAL) shell
