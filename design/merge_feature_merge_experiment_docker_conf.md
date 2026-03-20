# ConStrain Merge Design: feature_merge_experiment + docker_conf

## 1. Objective

Combine the new features on feature_merge_experiment with docker_conf (PR #105 Containerization) while preserving designed capabilities from both branches.

Primary goals:

- Preserve features from both branches as much as possible, especially feature design intent.
- Merge two frontend apps into one unified frontend.
- Keep strict frontend/backend separation through REST APIs.
- Adopt containerization from docker_conf as the baseline, with selective replacement if inefficient.
- Prefer true branch merge to preserve contributor history.

## 2. Scope

In scope:

- True merge of docker_conf into feature_merge_experiment.
- Unified frontend architecture and feature migration plan.
- Backend/API consolidation to support frontend and direct API consumers.
- docker-compose-first local/dev container runtime.
- Test and documentation updates for merged architecture.

Out of scope:

- Cloud deployment hardening beyond docker-compose local/dev baseline.
- Full deprecation/removal of legacy UI on day one.

## 3. Architectural Direction

### 3.1 Target System

- One primary web frontend aligned with current branch API-calling architecture.
- One REST API backend as canonical business interface.
- Optional PyQt desktop frontend retained temporarily as fallback client.
- Containerized runtime using docker_conf patterns, simplified where needed.

### 3.2 Frontend Strategy

Decision:

- Do not require Streamlit as target technology.
- Preserve Streamlit-designed user features/workflows by migrating them into the unified API-driven frontend.

Principles:

- Frontend remains orchestration/presentation only.
- Business logic, validation, and execution remain in backend APIs.
- No backend-coupled local logic in frontend that cannot be called via REST.

### 3.3 API Strategy

Decision:

- Breaking API changes are allowed to achieve cleaner merged design.

Principles:

- Keep API-first architecture so any client (web UI, CLI, external platform) uses same backend contract.
- Group APIs by domain (workflow, verification, reporting, jobs/status).
- Define explicit request/response schemas and validation behavior.
- Support long-running tasks with execution-status model suitable for web UX.

### 3.4 Containerization Strategy

Decision:

- Reuse docker_conf container setup as baseline.
- Replace components that are inefficient or operationally inconvenient.

Principles:

- docker-compose local/dev is first-class runtime.
- Standardize env var and volume path contracts.
- Prefer minimal service set for baseline run; enable optional extended services.
- Harden security around container orchestration patterns if frontend currently controls sibling containers.

## 4. Merge Strategy

### 4.1 Why merge-first

A true merge from docker_conf into feature_merge_experiment best preserves:

- Contribution history
- Existing implementation context
- Lower risk of unintentionally dropping collaborator work

### 4.2 Merge execution pattern

1. Perform true merge.
2. Resolve mechanical conflicts with minimal behavior change.
3. Resolve semantic conflicts by applying this design document priorities.
4. Validate feature retention against explicit feature matrix.

### 4.3 Conflict resolution priority

1. Data/API correctness
2. Feature preservation from both branches
3. Runtime stability in docker-compose
4. UX consistency in unified frontend
5. Codebase simplification and deprecation tagging

## 5. Unified Frontend Feature Migration

### 5.1 Preservation requirement

Every meaningful Streamlit feature/workflow from docker_conf must map to a corresponding capability in the unified frontend, even if UI controls and framework differ.

### 5.2 Migration approach

- Build a feature mapping matrix: Streamlit feature -> target unified frontend feature.
- Preserve user flow and output semantics.
- Ensure each migrated flow triggers backend via REST API calls only.
- Add parity tests for each critical migrated feature.

### 5.3 Desktop fallback handling

- Keep PyQt as optional path for one transition cycle.
- Minimize dual-maintenance by extracting shared logic to backend/service layers.
- Mark desktop-only UX as fallback, not primary evolution path.

## 6. Backend/API Consolidation Design

### 6.1 API shape

Target grouped domains:

- Workflow composition and validation
- Verification case generation and validation
- Execution submission
- Execution status/result retrieval
- Catalog/discovery

### 6.2 Contract quality

- Explicit schemas for all endpoints.
- Consistent validation and error structure.
- Observable operation states for long-running jobs.
- Clear separation between synchronous validation endpoints and asynchronous execution endpoints.

### 6.3 Non-UI consumers

- All operations available without frontend.
- CLI/external integrations call same REST APIs.
- No frontend-only execution path.

## 7. Container Architecture

### 7.1 Baseline

Adopt docker_conf compose/service structure initially.

Baseline profiles:

- Minimal: backend API + unified frontend
- Extended: additional processing/worker/reporting services as needed

### 7.2 Runtime contracts

Standardize:

- Environment variable names and defaults
- Mounted volume locations for inputs/resources/results
- Startup ordering and health checks
- Log locations and error visibility

### 7.3 Efficiency and convenience checks

Refactor if needed:

- Excessive Dockerfile duplication
- Oversized image dependencies
- Brittle path assumptions
- Operationally awkward startup flows

## 8. Implementation Plan (Step-by-Step)

### Phase A: Pre-merge Preparation

1. Snapshot branch diffs and identify high-risk conflict files.
2. Build a feature inventory from both branches (frontend, API, container).
3. Define acceptance matrix for feature preservation.

### Phase B: Merge + Triage

1. Execute true merge of docker_conf into feature_merge_experiment.
2. Resolve mechanical conflicts first.
3. Produce unresolved semantic conflict list for design-driven resolution.

### Phase C: Frontend Unification

1. Create unified frontend structure in current branch style.
2. Port Streamlit-designed workflows into unified frontend screens/flows.
3. Route all frontend actions through REST API calls.
4. Keep PyQt fallback functional with minimal incremental changes.

### Phase D: API Consolidation

1. Reorganize endpoints into clearer domain grouping.
2. Introduce execution state model for long-running workflows.
3. Align validation and error response schemas.
4. Update client callers (frontend + CLI adapters if needed).

### Phase E: Container Integration

1. Integrate docker_conf compose and Docker assets.
2. Harmonize env vars, path contracts, and service entrypoints.
3. Reduce inefficiencies identified in runtime and image design.
4. Validate minimal and extended compose profiles.

### Phase F: Validation and Documentation

1. Run regression and integration tests.
2. Execute end-to-end scenario in unified frontend and direct REST mode.
3. Update README/docs with new architecture and run instructions.
4. Add deprecation notes for legacy/superseded paths.

## 9. Verification Plan

Functional verification:

- Feature parity checks for migrated Streamlit design features.
- Unified frontend full flow tests.
- Direct REST API invocation tests for external/CLI consumers.

Runtime verification:

- docker-compose up/down reliability.
- Service health and startup correctness.
- Correct output artifact generation in mounted paths.

Regression verification:

- Existing core tests pass.
- New integration tests for merged flows pass.

## 10. Risks and Mitigations

Risk: semantic merge conflicts hide feature loss.
Mitigation: explicit feature matrix and mandatory parity sign-off.

Risk: endpoint changes break existing internal callers.
Mitigation: synchronize callers during same merge phase; add compatibility shims only when cost-effective.

Risk: container orchestration pattern introduces security/ops complexity.
Mitigation: harden compose defaults and move orchestration responsibility server-side where practical.

Risk: dual-frontend maintenance overhead.
Mitigation: keep PyQt fallback but freeze feature expansion there.

## 11. Deliverables

- Merged branch with docker_conf integrated.
- Unified API-driven primary frontend preserving Streamlit-designed features.
- Consolidated REST API contracts and execution model.
- docker-compose local/dev runtime with updated docs and tests.
- Migration notes and deprecation guidance.

## 12. Wish List (Out of Scope, Future Phases)

### Frontend Enhancements

- File upload support (multipart/form-data) - Replace path-based verification inputs with real file uploads for improved UX
- Dropdown/constrained UI controls - Replace free-text inputs with validated dropdowns for plot_option, log_level, report items
- Progress streaming - WebSocket or Server-Sent Events for real-time verification execution progress

### Testing and Validation

- Comprehensive error scenarios - API timeouts, invalid parameters, permission errors, malformed files
- End-to-end scenario tests - Real workflows from case file upload through artifact download
- Performance/load tests - Artifact listing and download with large file sets
- Manual acceptance checklist - Documented scenarios for human sign-off

### Documentation and Tooling

- Migration guide for contributors - Document architecture changes, new run commands, deprecated paths
- Troubleshooting runbook - Common issues and resolution steps for unified frontend + container runtime
- CLI adapter updates - Ensure CLI calls same REST APIs as web frontend

### Operational Hardening

- Authentication/authorization layer - Role-based access control if needed for multi-user deployments
- Audit logging - Track who accessed what artifacts and execution results
- Secret management improvements - Secure handling of API keys, credentials in containerized environment

### Containerization Polish

- Health check hardening - Comprehensive readiness probes for all services
- Resource limit tuning - Memory/CPU constraints for containers
- Extended compose profiles - Optional advanced services (caching, monitoring, worker scaling)

## 13. Phase 4: Containerization Adoption (In Progress)

### Phase C Status

✅ **Completed:**

- REST API endpoints for verification execution and artifact management
- Web UI wired to call backend REST APIs
- 8 integration tests for verification route and artifact downloads
- Feature mapping matrix and design documentation

**Remaining Phase C items (Wish List section 12):**

- File upload support (multipart/form-data)
- Dropdown/constrained UI controls
- Comprehensive error scenario tests

### Phase 4 Progress (Checkpoint 1: API Services)

**✅ Completed:**

1. **Dockerfile.api-server** - Unified backend API
   - Replaces separate workflow/verification/reporting services
   - Multi-stage build for minimal image size
   - Consolidates all business logic in single FastAPI service
   - Healthcheck on GET /health endpoint
   - Standardized environment variables: OUTPUT_DIR, LOG_LEVEL
   - Listens on port 8000

2. **Dockerfile.api-ui** - FastAPI web frontend
   - Replaces Streamlit service (eliminates docker socket security risk)
   - Lightweight FastAPI + Jinja2 templates
   - ✅ **Removes docker socket mount** (critical security improvement)
   - ✅ **No docker daemon installation** (eliminates DinD anti-pattern)
   - Healthcheck on GET /health endpoint
   - Configurable `CONSTRAIN_API_BASE_URL` via environment
   - Listens on port 8000 (mapped to 8080 via compose)

3. **Updated docker-compose.yml** - Simplified orchestration
   - api-server: Unified backend (port 8000)
   - api-ui: Web frontend (host port 8080 -> container port 8000)
   - Removed: workflow, verification, reporting, streamlit services
   - Added: Service health checks with dependencies
   - Improved network: bridge with explicit subnet (172.20.0.0/16)
   - Service discovery via DNS names

4. **Health check endpoints** - Added to both FastAPI apps
   - GET /health returns {"status": "ok", "service": "..."}
   - Enables container orchestration monitoring
   - Docker healthcheck directives configured

5. **Design documentation:**
   - phase4_containerization_audit.md - Security analysis and roadmap
   - Identified security risks (docker socket, DinD) - ALL FIXED
   - Efficiency issues documented (Dockerfile duplication)
   - Operability standards defined

**Commit:** c4485e4

### Remaining Phase 4 Work

1. **Phase 4.2: Base Image Creation** (Priority: HIGH)
   - New Dockerfile.base for shared dependencies
   - Reduces duplication across service images
   - Benefits: 50MB+ size reduction per service, faster builds

2. **Phase 4.3: Refined Service Dockerfiles**
   - Simplify workflow/verification/reporting to inherit from base
   - Apply consistent patterns

3. **Phase 4.4-4.6: Runtime Hardening**
   - User isolation (run as non-root)
   - Network policies
   - Secret management

4. **Phase 4.7: End-to-End Testing** (Requires Docker daemon)
   - Completed on 2026-03-20 against the compose-backed API/UI stack.
   - Verified web UI at <http://localhost:8080>
   - Ran mounted G36 verification case through the web UI
   - Confirmed artifacts were generated and downloadable from the host browser path
   - Verified no docker socket mounted
   - Verified services were networked properly

### Current Validation Notes

- The "8 integration tests" claim refers to the current API-first UI suite in `tests/test_ai_workflow_ui_integration.py`, which contains 8 endpoint-level integration tests for compose, verify, and artifact download flows.
- Legacy Streamlit runtime assets are retained only as deprecated fallback/reference material during the transition cycle. They are no longer part of the supported compose runtime.
- Backend async job submission and polling are now available for workflow and verification execution, and the FastAPI UI now uses that job model for both `/run` and `/verify`.
- A live compose-backed UI verification run succeeded using mounted sample data and produced 10 artifacts under `/data/results/e2e-ui`, including downloadable summary markdown and zip output.
- Public browser downloads now use a dedicated public API base URL instead of leaking the internal compose DNS hostname.

### Known Open Gaps

- Runtime hardening follow-up items remain open: non-root users, image vulnerability scanning, and stricter network policy controls.
- Legacy Streamlit code remains as archived fallback/reference material until feature-parity cleanup is complete.

### Security Improvements Summary

| Risk | Previous State | Current State | Status |
| ------ | --- | --- | --- |
| Docker socket mount | ✅ Mounted in Streamlit | ❌ No mounts in new setup | ✅ FIXED |
| Docker-in-Docker | ✅ Installed in container | ❌ Not installed | ✅ FIXED |
| Arbitrary code execution | ⚠️ Possible via socket | ❌ Not possible | ✅ FIXED |
| Service communication auth | ❌ None | ⚠️ Network isolation only | Partial (Enhanced) |

## 14. Decision Log (Confirmed)

- Merge style: true merge first.
- Primary frontend approach: current branch API-calling web style.
- Streamlit: feature design preserved, framework not required.
- Desktop GUI: keep optional fallback.
- Containerization: adopt docker_conf baseline and optimize where inefficient.
- API compatibility: breaking changes allowed if they improve merged architecture.
- **Phase 4 decision:** Use FastAPI for both backend API and web UI tier (not separate frameworks).
