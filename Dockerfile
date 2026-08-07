# syntax=docker/dockerfile:1
FROM node:22-alpine AS frontend
WORKDIR /frontend
COPY frontend/package.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

FROM python:3.12-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates unzip && rm -rf /var/lib/apt/lists/*
# Xray version is intentionally pinned; replace with a tested release before production.
ARG XRAY_VERSION=26.6.1
RUN curl -fsSL "https://github.com/XTLS/Xray-core/releases/download/v${XRAY_VERSION}/Xray-linux-64.zip" -o /tmp/xray.zip &&     unzip /tmp/xray.zip -d /usr/local/bin && chmod +x /usr/local/bin/xray && rm /tmp/xray.zip
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY backend ./backend
COPY --from=frontend /frontend/dist ./backend/app/static
COPY entrypoint.sh ./
RUN chmod +x entrypoint.sh && mkdir -p /data/xray
ENV XRAY_PATH=/usr/local/bin/xray
ENV XRAY_CONFIG=/data/xray/config.json
CMD ["./entrypoint.sh"]
