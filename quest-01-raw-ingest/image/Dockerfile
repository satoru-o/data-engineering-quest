FROM python:3.12-slim

RUN pip install --no-cache-dir \
      pandas==2.2.3 \
      pyarrow==18.1.0 \
      duckdb==1.1.3 \
      ipython==8.30.0

# breakpoint() でIPythonのデバッガに落ちるようにする。
# 書き途中のコードの真ん中で止めて、その場の変数を触れる
ENV PYTHONBREAKPOINT=IPython.terminal.debugger.set_trace
# コンテナは非rootのuidで動く。passwdに載っていないのでHOMEが / になり、
# IPythonが履歴ファイルを書けずに落ちる。書ける場所を明示しておく
ENV HOME=/tmp
ENV IPYTHONDIR=/tmp/.ipython

WORKDIR /app
COPY gen.py check.py replstart.py /app/

# 正解データの置き場。ホストにはマウントしない
RUN mkdir -p /truth && chmod 777 /truth

CMD ["python", "/app/check.py"]
