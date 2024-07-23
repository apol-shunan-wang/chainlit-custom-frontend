# https://hub.docker.com/_/python
FROM python:3.12.4-bookworm

WORKDIR /usr/src/server

# requirements.txtにリストされたパッケージをインストールする
RUN pip install --upgrade pip
ADD ./docker/main/chainlit/requirements.txt .
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# リモートデバッグ用パッケージをインストールする
RUN pip install --trusted-host pypi.python.org debugpy

# コンテナ起動後、FastAPIを実行し8000ポートで待機
# CMD ["python3", "-m", "debugpy", "--listen", "0.0.0.0:5678", "-m", "chainlit", "run", "app.py", "-w"]
CMD ["python3", "-m", "debugpy", "--listen", "0.0.0.0:5678", "-m", "uvicorn", "app:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
