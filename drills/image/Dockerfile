FROM python:3.12-slim

RUN pip install --no-cache-dir \
      pandas==2.2.3 \
      pyarrow==18.1.0 \
      duckdb==1.1.3 \
      numpy==2.2.1 \
      jupyterlab==4.3.4

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
