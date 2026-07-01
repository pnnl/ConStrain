# Docker Troubleshooting for ConStrain

This guide summarizes common operational issues observed during Phase 4 validation.

## 1) UI unreachable on port 8080

Symptoms:
- `curl http://localhost:8080/` fails or resets.

Checks:
```bash
docker-compose -f docker/docker-compose.yml ps
docker-compose -f docker/docker-compose.yml logs --tail=100 api-ui
```

Expected compose mapping:
- `8080:8000` for `api-ui`

Fix:
- Ensure `docker/docker-compose.yml` maps UI host port `8080` to container `8000`.

## 2) api-ui exits on startup with missing module

Symptoms:
- `api-ui` exits with `ModuleNotFoundError: No module named 'packaging'`.

Checks:
```bash
docker-compose -f docker/docker-compose.yml logs --tail=120 api-ui
```

Fix:
- Rebuild with current Dockerfile where runtime installs include `packaging`:
```bash
docker-compose -f docker/docker-compose.yml up -d --build
```

## 3) .env overrides not taking effect

Symptoms:
- Expected `LOG_LEVEL=DEBUG` but service still reports `LOG_LEVEL=INFO`.

Checks:
```bash
docker-compose -f docker/docker-compose.yml exec -T api-server env | grep LOG_LEVEL
```

Fix options:
- Run compose from `docker/` so default `.env` resolution picks up `docker/.env`.
- Or use explicit env file:
```bash
docker-compose --env-file docker/.env -f docker/docker-compose.yml up -d
```

## 4) Service-to-service calls fail

Symptoms:
- UI cannot call `api-server`.

Checks:
```bash
docker-compose -f docker/docker-compose.yml exec -T api-ui curl -sS http://api-server:8000/health
```

Fix:
- Verify both services are healthy and on the same compose network.
- Restart stack:
```bash
docker-compose -f docker/docker-compose.yml down
docker-compose -f docker/docker-compose.yml up -d
```

## 5) Verify volume mount behavior

Checks:
```bash
docker-compose -f docker/docker-compose.yml exec -T api-server touch /data/results/test-file.txt
ls -la docker/examples_results/test-file.txt
rm -f docker/examples_results/test-file.txt
```

Expected:
- File created inside container appears on host path.

## 6) Confirm security posture

Checks:
```bash
docker inspect constrain-api-ui --format '{{json .Mounts}}'
docker exec constrain-api-ui sh -c 'command -v docker || echo docker-not-installed'
```

Expected:
- No `/var/run/docker.sock` mount.
- `docker-not-installed` inside container.
