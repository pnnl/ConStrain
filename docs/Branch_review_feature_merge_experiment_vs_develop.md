# Branch review: `feature_merge_experiment` vs `develop`

This document summarizes what is implemented on **`feature_merge_experiment`** relative to **`develop`** (as of the review date). It is a narrative of the diff, not a merge checklist.

## Scope

- **Branch reviewed:** `feature_merge_experiment`
- **Baseline:** `develop`
- **Approximate diff:** 37 commits, 57 files changed, ~52,579 insertions / ~27 deletions (line count is dominated by example data and large JSON/CSV under `docker/examples/`).

---

## High-level themes

### Docker / containerization

- Multiple images and runners: workflow, verification, reporting, Streamlit UI, plus **Phase 4 “API-first”** stack (`docker/Dockerfile.api-server`, `docker/Dockerfile.api-ui`) orchestrated by `docker/docker-compose.yml`.
- Entry scripts: `docker/run_workflow.py`, `docker/run_verification.py`, `docker/run_reporting.py`; Streamlit app `docker/streamlit_app.py`.
- Operator docs: `docker/container_docs/`, `docker/README.md`, `docker/TESTING_PHASE4.md`, `docker/TROUBLESHOOTING.md`.
- Example assets: G36 workflow, verification cases, schema, and sample CSV under `docker/examples/`.

### AI workflow agent / composer

- New package area `constrain/ai/` (e.g. `workflow_composer.py`, `workflow_runner.py`, LLM client, schema utilities, introspection).
- User-facing docs: `docs/AI_Workflow_Composer_Design.md`, `docs/AI_Workflow_Composer_Overview.md`, `docs/Workflow_AI_User_Guide.md`.

### REST API and unified frontend path

- API surface extended/used for verification and related flows: `constrain/api/verification.py`, `constrain/api/reporting.py`, `constrain/api/workflow.py`.
- Dedicated AI workflow server and UI: `constrain/app/ai_workflow_server.py`, `constrain/app/ai_workflow_ui.py`.
- Verification **artifact** APIs and tests (`tests/test_ai_workflow_server_artifacts.py`); UI **wired to REST** for verification execution and artifacts (`tests/test_ai_workflow_ui_integration.py`).

### Library / backend fixes

- Changes in `constrain/libcases.py` (includes an aggregation-backend bugfix in branch history).

### Dependencies and tooling

- `pyproject.toml` / `uv.lock` updates (uv and additional dependencies).

### Design / merge documentation

- `design/frontend_feature_mapping_streamlit_to_unified.md`
- `design/merge_feature_merge_experiment_docker_conf.md`
- `design/phase4_containerization_audit.md`

### CI

- `.github/workflows/docker_test.yml` includes:
  - **API stack (Phase 4):** `docker-compose` build/up, health checks on host ports **8000** (API server) and **8080** (API UI), in-network health from the UI container, assertions that the API UI **does not** mount `docker.sock` or include the Docker CLI, and validation of **env overrides** via `docker/.env`.
  - **Workflow image:** build `Dockerfile.workflow`, run default demo, assert success string in logs.
  - **Verification image:** build, `--help`, run with example mounts, assert success string in logs.
  - **Reporting image:** build (after verification job), help and execution tests using verification outputs, plus `--log-level` acceptance.

### Tests

- Docker-focused tests: `tests/test_docker_workflow.py`, `tests/test_docker_verification.py`, `tests/test_docker_reporting.py`, `tests/test_docker_streamlit.py`.
- API test adjustments under `tests/api/`; shared fixtures in `tests/conftest.py`.

### Repository hygiene

- `.gitignore` updates; Black/formatting and test-stability commits in branch history.

---

## Commit arc (short narrative)

Early commits introduce **Docker images** for workflows, then **verification** and **reporting** containers, a **Streamlit** front end, logging instead of prints, and documentation. Mid-stream adds the **AI workflow agent**, uv/deps, workflow generation, and execution (WIP, then hardened). Later work **merges `docker_conf`**, adds **verification artifact APIs**, **integrates the web UI with the REST API**, **Phase 4** API-first Docker layout, compose/env overrides, design doc checkpoint updates, and **API-stack CI** checks.

---

## Large files note

Most inserted lines come from bundled examples, especially:

- `docker/examples/data/G36_Modelica_Jan.csv`
- `docker/examples/schema/library.json`

When reviewing PR size or blame, treat those as **fixture data**, not application logic.
