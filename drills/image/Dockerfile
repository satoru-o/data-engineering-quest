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

RUN uv sync --frozen --no-dev --package dequest-drills

ENV PATH="/opt/venv/bin:$PATH"

# 非rootのuidで動く。passwdに載っていないのでHOMEが / になり、
# Jupyterが設定や実行時ファイルを書けずに落ちる
ENV HOME=/tmp
ENV JUPYTER_CONFIG_DIR=/tmp/.jupyter
ENV JUPYTER_RUNTIME_DIR=/tmp/.jupyter/runtime

WORKDIR /work

CMD ["jupyter", "lab", \
     "--ip=0.0.0.0", "--port=8888", "--no-browser", \
     "--ServerApp.token=", "--ServerApp.password=", \
     "--ServerApp.root_dir=/work"]
