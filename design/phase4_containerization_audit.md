# Phase 4: Containerization Adoption - Audit and Refactor Plan

## Current State Analysis

### Docker Services (docker-compose.yml)

**Services identified:**
1. **workflow** - Executes ConStrain workflows from JSON
   - Image: constrain-workflow:latest
   - Dockerfile: docker/Dockerfile.workflow
   - Volumes: workflows, data, verification_cases, schema, results, weather, resources
   - Network: constrain-network

2. **verification** - Runs verification cases
   - Image: constrain-verification:latest
   - Dockerfile: docker/Dockerfile.verification
   - Volumes: data, verification_cases, schema, results, weather, resources, tolerances.json
   - Network: constrain-network

3. **reporting** - Generates summary reports
   - Image: constrain-reporting:latest
   - Dockerfile: docker/Dockerfile.reporting
   - Volumes: results
   - Depends on: verification
   - Network: constrain-network

4. **streamlit** - Web UI (DEPRECATED - needs replacement)
   - Image: constrain-streamlit:latest
   - Dockerfile: docker/Dockerfile.streamlit
   - Ports: 8501:8501
   - ⚠️ **SECURITY RISK**: Mounts docker socket at `/var/run/docker.sock`
   - ⚠️ **SECURITY RISK**: Docker daemon installed inside container
   - Network: constrain-network

### Issues Identified

#### 🔴 Critical Security Issues
1. **Docker-in-Docker Anti-Pattern**
   - Streamlit container installs Docker daemon (Dockerfile.streamlit line 11-14)
   - Mounts host docker socket (docker-compose.yml line 78)
   - Allows arbitrary code execution with host Docker access
   - **Fix**: Move execution orchestration to backend API tier; eliminate socket mount

2. **No Service-to-Service Authentication**
   - Services on constrain-network can call each other without auth
   - **Fix**: Add auth headers/tokens or move to authenticated API endpoints

#### 🟡 Efficiency Issues
1. **Dockerfile Duplication**
   - workflow, verification, reporting all use similar multi-stage pattern
   - Each does separate poetry export (redundant downloads)
   - **Fix**: Create base image with common dependencies, inherit in service images

2. **Large Base Images**
   - Using python:3.10-slim (but still 120MB+)
   - Multiple apt package installations per Dockerfile
   - **Fix**: Consider distroless Python or Alpine-based images

3. **Redundant Volume Mounts**
   - weather, resources, tolerances.json mounted in multiple services
   - **Fix**: Consider putting in base image or shared volume

4. **No Health Checks**
   - Services lack health monitoring
   - **Fix**: Add healthcheck directives for all services

#### 🟡 Operability Issues
1. **Hardcoded Paths**
   - `/app` paths hardcoded throughout
   - Results directory `/app/results` or `examples_results`
   - **Fix**: Use environment variables for output paths

2. **Inconsistent Environment Setup**
   - PYTHONPATH set inconsistently
   - No LOG_LEVEL, DEBUG environment variables
   - **Fix**: Standardize env vars across all services

3. **No Logging Configuration**
   - Services write to stdout but no log routing configured
   - **Fix**: Add docker logging driver configuration

4. **Missing Resource Limits**
   - No memory or CPU constraints
   - **Fix**: Set reasonable limits per service

5. **No Service Discovery**
   - Hardcoded container names assumed for networking
   - **Fix**: Use DNS names within network

### Current Dockerfile Patterns

All computation services (workflow, verification, reporting) use:
```
FROM python:3.10-slim as builder
  → Install build deps + poetry
  → Extract requirements (excluding PyQt6)
  → Pip install everything

FROM python:3.10-slim
  → Copy packages from builder
  → Copy source code
  → Set PYTHONPATH
```

## Refactoring Plan

### Phase 4.1: Replace Streamlit with FastAPI Web Tier ✅ Prerequisite Complete
- ✅ Phase C delivered ai_workflow_ui.py (FastAPI + Jinja2 templates)
- ✅ REST endpoints in ai_workflow_server.py
- Required: New Dockerfile.api-ui service for web tier

### Phase 4.2: Create Base Image (Priority: HIGH)

**New file: docker/Dockerfile.base**
```dockerfile
FROM python:3.10-slim

# Install system dependencies once
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl gcc g++ ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Python build tools
RUN pip install --no-cache-dir poetry poetry-plugin-export

WORKDIR /app
```

**Benefits:**
- Reduces image size duplication (saves ~50MB per service)
- Faster builds (base layers cached)
- Consistent Python runtime

### Phase 4.3: Consolidate and Simplify Dockerfiles

**New files:**
- `docker/Dockerfile.api-ui` - FastAPI web tier (replaces Streamlit, removes docker socket)
- `docker/Dockerfile.api-server` - Backend API tier (consolidates verification + reporting)
- Simplify workflow/verification/reporting to inherit from base

**Changes:**
- Remove docker socket mount
- Remove docker daemon installation
- Add healthcheck directives
- Use environment variables for paths

### Phase 4.4: Update docker-compose.yml

**New structure:**
```yaml
services:
  api-server:
    # Runs verification, reporting, workflows
    # No docker socket mount
    # Has healthcheck
    ports:
      - "8000:8000"
    environment:
      - OUTPUT_DIR=/data/results
      - LOG_LEVEL=INFO

  api-ui:
    # FastAPI web frontend
    # Calls api-server via REST only
    ports:
      - "8080:8080"  # or 8000 if separate port not needed
    depends_on:
      - api-server
    environment:
      - API_BASE_URL=http://api-server:8000
      - LOG_LEVEL=INFO

  # Optional: extended profile services
  (monitoring, caching, worker pool)
```

**Benefits:**
- Clean separation: orchestration in API, not UI
- Web tier stateless and scalable
- No docker socket needed
- Clear service dependencies

### Phase 4.5: Standardize Runtime Contracts

**Environment variables (across all services):**
- `LOG_LEVEL` - INFO, DEBUG, WARNING (default: INFO)
- `OUTPUT_DIR` - Results output path (default: /data/results)
- `API_BASE_URL` - Backend endpoint for UI (default: http://localhost:8000)
- `CONSTRAIN_LLM_API_BASE` - LLM endpoint for ai_workflow_composer
- `CONSTRAIN_LLM_MODEL` - LLM model name

**Health check paths:**
- `GET /health` - All services expose readiness
- `GET /health/ready` - Ready for requests
- `GET /health/live` - Process alive

**Output contracts:**
- Results always written to `${OUTPUT_DIR}` (no guessing paths)
- Artifacts accessible via GET /artifacts API
- Structured JSON responses

### Phase 4.6: Security Hardening

1. ✅ **Remove docker socket mount** - Move orchestration server-side
2. ✅ **Eliminate docker-in-docker** - No docker daemon in containers
3. 📋 **Add user isolation** - Run services as non-root user
4. 📋 **Scan images for vulnerabilities** - trivy scan or grype
5. 📋 **Implement network policies** - Restrict service-to-service communication

### Phase 4.7: Testing and Validation

**Checklist:**
- [ ] `docker-compose up` starts all services without errors
- [ ] Web UI accessible at http://localhost:8080
- [ ] API server healthcheck passes: `curl http://localhost:8000/health`
- [ ] Run verification case end-to-end through web UI
- [ ] Artifacts generated and downloadable
- [ ] No docker socket mounted in running containers
- [ ] No docker daemon running inside containers
- [ ] Services properly networked (can call each other via DNS)

## Implementation Priority

**Immediate (Phase 4):**
1. Create Dockerfile.api-ui for FastAPI web tier
2. Update docker-compose.yml to remove docker socket, use FastAPI service
3. Add healthchecks to all services
4. Define consistent env vars (OUTPUT_DIR, LOG_LEVEL, API_BASE_URL)
5. Test docker-compose orchestration end-to-end

**Follow-up (Phase 5):**
1. Create base Dockerfile to reduce duplication
2. Consolidate service Dockerfiles
3. Add user isolation and security scanning
4. Performance optimization (image size, startup time)

## Risk Mitigation

**Risk:** Removing docker socket breaks existing workflows.
- **Mitigation:** New backend API fully replaces orchestration from web tier. Old Streamlit removed. No workflows depend on container-launched jobs from UI.

**Risk:** API-server becomes single point of failure.
- **Mitigation:** (Future) Add worker scaling and job queue; for now, document manual restart procedure.

**Risk:** Services can't find each other on network.
- **Mitigation:** Use service names in docker-compose (not container_name); use DNS discovery (default in compose v3).

## Decision Log

- **Web Tier Technology:** FastAPI + Jinja2 templates (already done in Phase C)
- **Containerization Approach:** Composable microservices, no docker socket mount
- **Init Image:** python:3.10-slim (acceptable for now; Alpine upgrade deferred)
- **Orchestration:** Backend API-driven, not frontend-driven
- **Output Paths:** Standardized via environment variables
