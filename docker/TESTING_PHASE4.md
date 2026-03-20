# Phase 4: Docker Setup Testing Plan

## Prerequisites

Before running tests, ensure:
- Docker daemon is running (`docker ps` returns container list)
- docker-compose is installed (`docker-compose --version`)
- You have sufficient disk space (base images ~300-500MB)
- Port 8000 and 8080 are available on localhost

## Test Phase 4.1: Docker Image Build

### 4.1.1 Validate Dockerfile Syntax

```bash
cd docker

# Check api-server Dockerfile
docker build --no-cache -f Dockerfile.api-server -t constrain-api-server:test ..

# Check api-ui Dockerfile  
docker build --no-cache -f Dockerfile.api-ui -t constrain-api-ui:test ..

# Verify images were created
docker images | grep constrain-api
```

**Expected Results:**
- ✅ Both Dockerfiles build without errors
- ✅ constrain-api-server:test created (should be ~400-500MB)
- ✅ constrain-api-ui:test created (should be ~300-400MB)

### 4.1.2 Verify Image Contents

```bash
# Check api-server image has required modules
docker run --rm constrain-api-server:test python -c "import constrain.app.ai_workflow_server; print('API server module OK')"

# Check api-ui image has required modules
docker run --rm constrain-api-ui:test python -c "import constrain.app.ai_workflow_ui; print('API UI module OK')"
```

**Expected Results:**
- ✅ Both imports succeed
- ✅ Modules print OK messages

## Test Phase 4.2: Docker Compose Orchestration

### 4.2.1 Start Services

```bash
cd docker

# Start all services in background
docker-compose up -d

# Wait 10 seconds for services to initialize
sleep 10

# Check service status
docker-compose ps
```

**Expected Results:**
```
NAME                       STATUS
constrain-api-server       Up X seconds (health: starting)
constrain-api-ui           Up X seconds (health: starting)
```

### 4.2.2 Health Check Verification

```bash
# Wait for healthchecks to complete (after ~15 seconds)
sleep 10

# Check api-server health
curl http://localhost:8000/health

# Check api-ui health
curl http://localhost:8080/health
```

**Expected Results:**
```
{"status":"ok","service":"constrain-api-server"}
{"status":"ok","service":"constrain-api-ui"}
```

### 4.2.3 Verify Service Container Status

```bash
# Get detailed status
docker-compose ps

# Check healthcheck status in compose output
docker ps --format "table {{.Names}}\t{{.Status}}"
```

**Expected Results:**
- api-server: Running, health check passing
- api-ui: Running, health check passing

## Test Phase 4.3: Network Connectivity

### 4.3.1 Test Service-to-Service Communication

```bash
# From api-ui container, verify it can reach api-server
docker-compose exec api-ui curl -s http://api-server:8000/health | jq .

# Should return:
# {"status":"ok","service":"constrain-api-server"}
```

**Expected Results:**
- ✅ api-ui can call api-server via DNS name
- ✅ JSON response received and parsed

### 4.3.2 Test External Access

```bash
# Test from host machine
curl -v http://localhost:8080/

# Should return HTML form page (or 200 status)
```

**Expected Results:**
- ✅ HTTP 200 response
- ✅ HTML content returned (ConStrain AI Workflow Composer page)

## Test Phase 4.4: Security Verification

### 4.4.1 Verify No Docker Socket Mount

```bash
# Inspect api-ui container mounts
docker inspect constrain-api-ui | jq '.[] | .Mounts'

# Should NOT show /var/run/docker.sock
```

**Expected Results:**
```
[
  {
    "Type": "bind",
    "Source": "...",
    "Destination": "/app/constrain/app/templates",
    ...
  }
]
# NO mount with docker.sock!
```

### 4.4.2 Verify No Docker Daemon Inside Containers

```bash
# Try to run docker inside api-server
docker-compose exec api-server which docker

# Should return "docker not found" or empty
# (not executable)
```

**Expected Results:**
- ✅ Docker not found inside container
- ✅ No docker daemon running

### 4.4.3 Verify Containers Run as Accessible User (if configured)

```bash
# Check user inside container
docker-compose exec api-server whoami
docker-compose exec api-ui whoami

# Should return "root" (for now) or configured non-root user
```

**Expected Results:**
- ✅ Returns valid user (root or configured)

## Test Phase 4.5: API Functionality

### 4.5.1 Test Workflow Suggestion Endpoint

```bash
curl -X POST http://localhost:8000/ai/workflow/suggest \
  -H "Content-Type: application/json" \
  -d '{
    "goal_description": "Test workflow creation"
  }'

# Note: May fail if LLM not configured (this is expected)
```

**Expected Results:**
- ✅ HTTP 503 if LLM not configured (with proper error message)
- ✅ HTTP 200 with workflow data if LLM configured

### 4.5.2 Test Health Endpoints

```bash
# API server health
curl http://localhost:8000/health

# API UI health  
curl http://localhost:8080/health
```

**Expected Results:**
```json
{"status":"ok","service":"constrain-api-server"}
{"status":"ok","service":"constrain-api-ui"}
```

### 4.5.3 Test Artifact List Endpoint

```bash
curl 'http://localhost:8000/ai/artifacts/list?output_dir=/data/results'

# May return empty list if no results yet (this is OK)
```

**Expected Results:**
- ✅ HTTP 200
- ✅ JSON response with artifacts array

## Test Phase 4.6: Data Volume Mounting

### 4.6.1 Verify Results Directory

```bash
# Check if results directory exists
ls -la docker/examples_results/

# Check from inside container
docker-compose exec api-server ls -la /data/results/
```

**Expected Results:**
- ✅ Directory exists and is writable

### 4.6.2 Write Test File

```bash
# Create test file in container results
docker-compose exec api-server touch /data/results/test-file.txt

# Verify file exists on host
ls -la docker/examples_results/test-file.txt

# Clean up
rm docker/examples_results/test-file.txt
```

**Expected Results:**
- ✅ File created in container appears on host
- ✅ Bidirectional mount working

## Test Phase 4.7: Environment Variable Configuration

### 4.7.1 Verify Environment Variables

```bash
# Check api-server environment
docker-compose exec api-server env | grep -E "LOG_LEVEL|OUTPUT_DIR|PYTHONPATH"

# Check api-ui environment
docker-compose exec api-ui env | grep -E "LOG_LEVEL|CONSTRAIN_API_BASE"
```

**Expected Results:**
```
LOG_LEVEL=INFO
OUTPUT_DIR=/data/results
PYTHONPATH=/app
CONSTRAIN_API_BASE_URL=http://api-server:8000
```

### 4.7.2 Test Environment Variable Overrides

```bash
# Create override .env file
cat > docker/.env << EOF
LOG_LEVEL=DEBUG
CONSTRAIN_API_BASE_URL=http://api-server:8000
EOF

# Restart services
docker-compose down
docker-compose up -d

# Verify override
docker-compose exec api-server env | grep LOG_LEVEL
# Should show: LOG_LEVEL=DEBUG
```

**Expected Results:**
- ✅ .env file is read
- ✅ Variables overridden correctly
- ✅ Services restart successfully

## Test Phase 4.8: Service Dependencies and Startup Order

### 4.8.1 Verify Startup Order

```bash
# Stop all services
docker-compose down

# Start fresh
docker-compose up -d

# Check order of startup (api-server starts first)
docker-compose logs | head -50
```

**Expected Results:**
- ✅ api-server logs appear before api-ui logs
- ✅ api-ui waits for api-server healthcheck
- ✅ Both services eventually reach healthy state

### 4.8.2 Test Partial Failure Recovery

```bash
# Stop api-server only
docker-compose stop api-server

# Try to access api-ui (should fail to call backend)
curl http://localhost:8080/

# Restart api-server
docker-compose start api-server
sleep 5

# Try again (should work)
curl http://localhost:8080/
```

**Expected Results:**
- ✅ api-ui responds but backend calls fail gracefully
- ✅ After api-server restart, full functionality returns

## Test Phase 4.9: Cleanup

```bash
# Stop and remove containers
docker-compose down

# Remove images (optional)
docker rmi constrain-api-server:latest constrain-api-ui:latest

# Verify cleanup
docker ps | grep constrain
docker images | grep constrain
```

**Expected Results:**
- ✅ No containers running
- ✅ Images removed (if requested)

## Troubleshooting

### Images won't build
```bash
# Check Docker disk space
docker system df

# Remove old images
docker system prune -a

# Rebuild
docker-compose build --no-cache
```

### Services won't start
```bash
# Check logs
docker-compose logs api-server
docker-compose logs api-ui

# Verify ports are free
lsof -i :8000
lsof -i :8080

# Kill processes using ports
kill -9 <PID>
```

### Healthchecks failing
```bash
# Check healthcheck manually
docker-compose exec api-server curl http://localhost:8000/health

# Check endpoint exists
docker-compose exec api-server python -c "from constrain.app.ai_workflow_server import app; print(list(app.routes))"
```

### Services can't communicate
```bash
# Verify network exists
docker network ls | grep constrain

# Inspect network
docker network inspect docker_constrain-network

# Test DNS resolution from container
docker-compose exec api-ui nslookup api-server
```

## Success Criteria

✅ All tests pass if:
- [x] Both Dockerfiles build successfully
- [x] docker-compose up creates healthy services
- [x] Health endpoints respond with 200 OK
- [x] No docker socket mounts visible
- [x] No docker daemon inside containers
- [x] Service-to-service communication works
- [x] External access to web UI works
- [x] API endpoints are functional
- [x] Data volumes mount correctly
- [x] Environment variables are applied
- [x] Startup order respected
- [x] Graceful failure handling

## Execution Results (2026-03-20)

- Updated compose mapping for UI to `8080:8000` to match Uvicorn listener.
- Removed obsolete compose `version` key.
- Added runtime `packaging` dependency to API UI image to prevent startup crash.
- Enabled compose env overrides via `${VAR:-default}` for `LOG_LEVEL` and `CONSTRAIN_API_BASE_URL`.
- Validated backend-dependent UI behavior: UI page renders while backend is down and verify route returns handled error text.

## Post-Test Checklist

After successful testing:
- [x] Document any deployed differences from expected
- [x] Update docker/README.md with quick-start
- [x] Create troubleshooting guide for operators
- [x] Update CI/CD pipeline if needed
- [x] Tag commit with "phase-4-docker-validated"
