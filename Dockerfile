FROM alpine:3.8
LABEL maintainer="clewis@iqt.org"

RUN apk upgrade --no-cache && \
    apk add --no-cache \
    build-base \
    curl \
    python3 \
    python3-dev \
    py3-paramiko \
    tini \
    yaml-dev && \
    pip3 install --no-cache-dir --trusted-host pypi.python.org --upgrade pip && \
    rm -rf /var/cache/* && \
    rm -rf /root/.cache/*

# healthcheck
COPY healthcheck /healthcheck
RUN pip3 install -r /healthcheck/requirements.txt
ENV FLASK_APP /healthcheck/hc.py
HEALTHCHECK --interval=15s --timeout=15s \
 CMD curl --silent --fail http://localhost:5000/healthcheck || exit 1

COPY . /poseidon
WORKDIR /poseidon
ENV PYTHONPATH /poseidon/p:$PYTHONPATH
ENV POSEIDON_CONFIG /poseidon/config/poseidon.config

# install dependencies of poseidon modules for poseidon
RUN find . -name requirements.txt -type f -exec pip3 install -r {} \;

ENV PYTHONUNBUFFERED 0
ENV SYS_LOG_HOST NOT_CONFIGURED
ENV SYS_LOG_PORT 514

EXPOSE 9304

CMD (flask run > /dev/null 2>&1) & (tini -s -- /usr/bin/python3 /poseidon/p/poseidon.py)
