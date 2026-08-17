FROM python:3.12-slim

# 依存はリポジトリルートの pyproject.toml と uv.lock で決まる。
# ここに教材のバージョンは書かない。
#
# uv は PyPI から入れる。ghcr.io の公式イメージから COPY するほうが速いが、
# レジストリを2つに増やすとどちらかが落ちただけでビルドできなくなる。
# 依存パッケージと同じ経路だけで済ませる
RUN pip install --no-cache-dir uv==0.12.3

ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT=/opt/venv

WORKDIR /repo
# uv.lock はワークスペース全体を覆うので、全メンバーの pyproject.toml が要る
COPY pyproject.toml uv.lock .python-version ./
COPY drills/pyproject.toml drills/
COPY tutorial-01-pos-pipeline/pyproject.toml tutorial-01-pos-pipeline/
COPY tutorial-02-roster-cleaning/pyproject.toml tutorial-02-roster-cleaning/
COPY quest-01-raw-ingest/pyproject.toml quest-01-raw-ingest/
COPY quest-02-access-log-transform/pyproject.toml quest-02-access-log-transform/

RUN uv sync --frozen --no-dev --package dequest-quest01

ENV PATH="/opt/venv/bin:$PATH"

# breakpoint() でIPythonのデバッガに落ちるようにする。
# 書き途中のコードの真ん中で止めて、その場の変数を触れる
ENV PYTHONBREAKPOINT=IPython.terminal.debugger.set_trace
# コンテナは非rootのuidで動く。passwdに載っていないのでHOMEが / になり、
# IPythonが履歴ファイルを書けずに落ちる。書ける場所を明示しておく
ENV HOME=/tmp
ENV IPYTHONDIR=/tmp/.ipython

WORKDIR /app
# ビルドコンテキストがリポジトリルートなので、パスはルートからになる
COPY quest-01-raw-ingest/image/gen.py \
     quest-01-raw-ingest/image/check.py \
     quest-01-raw-ingest/image/replstart.py /app/

# 正解データの置き場。ホストにはマウントしない
RUN mkdir -p /truth && chmod 777 /truth

CMD ["python", "/app/check.py"]
