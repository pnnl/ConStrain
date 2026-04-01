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
docker compose -f docker/docker-compose.yml up -d --build
docker compose -f docker/docker-compose.yml ps
curl http://localhost:8000/health
curl http://localhost:8080/health
```

Stop services:

```bash
docker compose -f docker/docker-compose.yml down
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
docker compose up -d
```

On Linux hosts, setting `APP_UID` and `APP_GID` to the current user avoids permission issues on the bind-mounted `docker/examples_results` directory while keeping the application processes non-root.

## Verification and Artifacts

The UI verification form at `http://localhost:8080/verify` is synchronous. A request is expected to run to completion before a new verification is submitted.

Primary Docker path convention:

- Host shared root: `../user_io`
- Container shared root: `/user_io`
- Example inputs: `/user_io/examples/input/...`
- Example outputs: `/user_io/examples/output/...`

The compose file keeps legacy `/data/...` mounts during migration, but new usage should prefer `/user_io/...` paths.

Example verification request through UI endpoint:

```bash
curl -fsS -X POST http://localhost:8080/verify \
  --data-urlencode 'case_file_path=/user_io/examples/input/verification_cases/G36_library_verification_cases.json' \
  --data-urlencode 'output_dir=/user_io/examples/output/manual-run' \
  --data-urlencode 'data_file_path=/user_io/examples/input/data/G36_Modelica_Jan.csv' \
  --data-urlencode 'library_json_path=/user_io/examples/input/schema/library.json' \
  --data-urlencode 'plot_option=all-compact' \
  --data-urlencode 'fig_width=6.4' \
  --data-urlencode 'fig_height=4.8' \
  --data-urlencode 'log_level=INFO' \
  --data-urlencode 'summary_file_name=verification_summary.md' \
  --data-urlencode 'generate_summary=on'
```

Artifact endpoints exposed by `api-server`:

```bash
curl "http://localhost:8000/ai/artifacts/list?output_dir=/user_io/examples/output/manual-run&recursive=true"
curl -L -o verification_summary.md "http://localhost:8080/artifact/download?output_dir=/user_io/examples/output/manual-run&relative_path=verification_summary.md"
curl -L -o verification_results.zip "http://localhost:8080/artifact/download-zip?output_dir=/user_io/examples/output/manual-run"
```

## Notes

- UI host port is `8080` mapped to container port `8000`.
- Backend API is exposed on host port `8000`.
- No Docker socket is mounted in containers.
- Container health checks and in-network probes use Python stdlib HTTP calls, so the runtime images do not need `curl`.
- Legacy Streamlit Docker assets are deprecated and retained only as archived reference material.
