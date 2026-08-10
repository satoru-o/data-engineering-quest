FROM python:3.12-slim

RUN pip install --no-cache-dir \
      pandas==2.2.3 \
      pyarrow==18.1.0 \
      duckdb==1.1.3

WORKDIR /app
COPY gen.py check.py /app/

# 正解データの置き場。ホストにはマウントしない
RUN mkdir -p /truth && chmod 777 /truth

CMD ["python", "/app/check.py"]
