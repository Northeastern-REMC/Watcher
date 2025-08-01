FROM python:3.12.6-alpine AS builder 

RUN apk update
RUN apk add g++ unixodbc-dev
ADD https://astral.sh/uv/install.sh /uv-installer.sh

ENV UV_INSTALL_DIR="/root/.local/bin/"
ENV PATH="/root/.local/bin/:$PATH"

RUN sh /uv-installer.sh
RUN rm /uv-installer.sh

RUN apk --no-cache add curl gnupg
WORKDIR /watcher

COPY . .

RUN curl -O https://download.microsoft.com/download/7/6/d/76de322a-d860-4894-9945-f0cc5d6a45f8/msodbcsql18_18.4.1.1-1_amd64.apk
RUN curl -O https://download.microsoft.com/download/7/6/d/76de322a-d860-4894-9945-f0cc5d6a45f8/mssql-tools18_18.4.1.1-1_amd64.apk

FROM python:3.12.6-alpine AS main
LABEL Maintainer="Karsten Courtney <k_courtney@nremc.com>"
LABEL org.opencontainers.image.source="https://github.com/Northeastern-REMC/Watcher"
LABEL Description="Website meant to read battery alarm and fault errors"

WORKDIR /watcher

COPY --from=builder /watcher/msodbcsql18_18.4.1.1-1_amd64.apk .
COPY --from=builder /watcher/mssql-tools18_18.4.1.1-1_amd64.apk .
RUN apk add --allow-untrusted msodbcsql18_18.4.1.1-1_amd64.apk
RUN apk add --allow-untrusted mssql-tools18_18.4.1.1-1_amd64.apk

RUN apk update
RUN apk add unixodbc-dev g++

COPY . .

ADD https://astral.sh/uv/install.sh /uv-installer.sh

ENV UV_INSTALL_DIR="/root/.local/bin/"
ENV PATH="/root/.local/bin/:$PATH"

RUN sh /uv-installer.sh
RUN rm /uv-installer.sh
RUN uv lock
RUN uv sync --locked

ENV PATH=/watcher/.venv/bin:$PATH
EXPOSE 8080

CMD ["gunicorn", "--worker-tmp-dir", "/dev/shm", "--bind", "0.0.0.0:8080", "watcher:ignite()"]