FROM ubuntu:24.04
ENV MODE dev
ENV DEBIAN_FRONTEND=noninteractive
ENV PIP_BREAK_SYSTEM_PACKAGES=1

RUN set -eux; \
    sed -i 's|http://ports.ubuntu.com|https://ports.ubuntu.com|g' /etc/apt/sources.list; \
    for i in 1 2 3 4 5; do \
        if apt-get update -o Acquire::Retries=5 -o Acquire::http::Timeout=30 -o Acquire::https::Timeout=30; then \
            break; \
        fi; \
        echo "apt-get update failed (attempt $i), retrying..." >&2; \
        sleep 10; \
    done; \
    apt-get install --no-install-recommends -yq \
      build-essential \
      python3 \
      python3-dev \
      python3-pip \
      libpq-dev \
      gdal-bin \
      libgdal-dev \
      make \
      npm \
      cron \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . /app
COPY etc/crontab /etc/crontab
RUN chmod 600 /etc/crontab

RUN cd frontend && npm ci && npm run build && cd ..

RUN pip3 install pipenv
RUN if [ "$MODE" = "production" ]; then \
        pipenv requirements --keep-outdated > requirements.txt; \
    elif [ "$MODE" = "dev" ]; then \
        pipenv requirements --dev > requirements.txt; \
    fi

RUN pip3 install --ignore-installed -r requirements.txt
