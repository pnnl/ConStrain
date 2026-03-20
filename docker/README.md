# Docker Configuration for ConStrain

This directory contains Docker assets for the API-first ConStrain runtime.

## Services

- `api-server`: Unified backend API for workflow composition, verification execution, and artifact management.
- `api-ui`: FastAPI + Jinja web UI that calls the backend API.

## Key Files

- `Dockerfile.api-server`
- `Dockerfile.api-ui`
- `docker-compose.yml`
- `TESTING_PHASE4.md`
- `TROUBLESHOOTING.md`

## Quick Start

From repository root:

```bash
docker-compose -f docker/docker-compose.yml up -d --build
docker-compose -f docker/docker-compose.yml ps
curl http://localhost:8000/health
curl http://localhost:8080/health
```

Stop services:

```bash
docker-compose -f docker/docker-compose.yml down
```

## Environment Overrides

Compose supports defaults and `.env` overrides for:

- `LOG_LEVEL` (default `INFO`)
- `CONSTRAIN_API_BASE_URL` (default `http://api-server:8000`) for server-side UI-to-API calls inside Compose
- `CONSTRAIN_PUBLIC_API_BASE_URL` (default `http://localhost:8000`) for browser-facing artifact download redirects
- `APP_UID` / `APP_GID` (default `1000`) to run the API containers as a non-root user that matches the host on Linux

Example override (from `docker/` directory):

```bash
printf 'LOG_LEVEL=DEBUG\nCONSTRAIN_API_BASE_URL=http://api-server:8000\nCONSTRAIN_PUBLIC_API_BASE_URL=http://localhost:8000\nAPP_UID=%s\nAPP_GID=%s\n' "$(id -u)" "$(id -g)" > .env
docker-compose up -d
```

On Linux hosts, setting `APP_UID` and `APP_GID` to the current user avoids permission issues on the bind-mounted `docker/examples_results` directory while keeping the application processes non-root.

## Notes

- UI host port is `8080` mapped to container port `8000`.
- Backend API is exposed on host port `8000`.
- No Docker socket is mounted in containers.
- Legacy Streamlit Docker assets are deprecated and retained only as archived reference material.
