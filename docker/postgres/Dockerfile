# https://hub.docker.com/_/postgres
FROM postgres:15.4-alpine

# 言語の設定
ENV LANG ja_JP.utf8

# 設定ファイルを/etc/postgresql以下にコピー
COPY ./docker/postgres/postgresql.conf /etc/postgresql/postgresql.conf

# config_fileを/etc/postgresql/postgresql.confに指定
CMD ["-c", "config_file=/etc/postgresql/postgresql.conf"]
