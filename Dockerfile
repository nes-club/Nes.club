FROM node:20-slim AS frontend-builder

WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build


FROM python:3.12
ENV MODE=dev
ENV PIP_BREAK_SYSTEM_PACKAGES=1

WORKDIR /app

COPY . /app

COPY --from=frontend-builder /app/frontend/static/dist/ /app/frontend/static/dist/
COPY --from=frontend-builder /app/frontend/webpack-stats.json /app/frontend/webpack-stats.json

RUN pip3 install pipenv
RUN if [ "$MODE" = "production" ]; then \
        pipenv requirements --keep-outdated > requirements.txt; \
    elif [ "$MODE" = "dev" ]; then \
        pipenv requirements --dev > requirements.txt; \
    fi

RUN pip3 install --ignore-installed -r requirements.txt
