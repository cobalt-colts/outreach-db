# syntax=docker/dockerfile:1

FROM oven/bun:1.3.14 AS frontend-builder

WORKDIR /app

COPY package.json bun.lock ./
RUN bun install --frozen-lockfile

COPY src ./src
COPY static ./static
COPY tsconfig.json vite.config.ts .npmrc ./
RUN bun run build


FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS python-builder

WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project


FROM node:22-bookworm-slim AS node-runtime


FROM python:3.13-slim-bookworm AS runtime

WORKDIR /app

ENV PATH="/app/.venv/bin:$PATH" \
    NODE_ENV=production \
    HOST=0.0.0.0 \
    PORT=3000 \
    API_ORIGIN=http://127.0.0.1:8000 \
    JWT_PRIVATE_KEY_PATH=/app/conf/jwt_private.pem \
    JWT_PUBLIC_KEY_PATH=/app/conf/jwt_public.pem \
    PYTHONUNBUFFERED=1

COPY --from=node-runtime /usr/local/bin/node /usr/local/bin/node
COPY --from=python-builder /app/.venv ./.venv
COPY --from=frontend-builder /app/build ./build

COPY app ./app
COPY main.py ./main.py
COPY docker/serve.py ./docker/serve.py

RUN groupadd --system outreach \
    && useradd --system --gid outreach --home-dir /app outreach \
    && mkdir -p /app/conf \
    && chown -R outreach:outreach /app

USER outreach

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD ["node", "-e", "Promise.all([fetch('http://127.0.0.1:3000/'),fetch('http://127.0.0.1:8000/openapi.json')]).then(rs=>{if(rs.some(r=>!r.ok))process.exit(1)}).catch(()=>process.exit(1))"]

CMD ["python", "docker/serve.py"]
