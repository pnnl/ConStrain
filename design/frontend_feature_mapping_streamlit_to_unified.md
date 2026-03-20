# Frontend Feature Mapping: docker_conf Streamlit -> Unified API Frontend

## Goal

Track one-to-one preservation of user-facing features from `docker/streamlit_app.py` into the unified API-driven frontend.

## Feature Mapping Matrix

| Streamlit Feature (docker_conf) | Existing Coverage in Current Frontend | Target Unified Frontend Behavior | Backend/API Contract Needed | Status |
| --- | --- | --- | --- | --- |
| CSV upload (required) | Partial (`/compose` text/json forms only) | File upload control with validation and clear status | `POST /ai/verification/execute` with `data_file_path` or multipart follow-up | In Progress |
| Verification case JSON upload (required) | Not present | File upload with required validation and preview | `POST /ai/verification/execute` `case_file_path` | In Progress |
| Optional library JSON upload | Not present | Optional custom library picker with fallback to default library | `POST /ai/verification/execute` `library_json_path` | In Progress |
| Upload readiness panel | Not present | Inline readiness indicators before run | Frontend state + preflight validation endpoint (optional) | Planned |
| Advanced options toggle | Not present | Expandable advanced settings panel | Existing execute payload fields | Planned |
| Plot options selector | Not present | Dropdown with same options | `plot_option` in verification execute request | Implemented in API |
| Figure size controls | Not present | Width/height numeric controls | `fig_size` in verification execute request | Implemented in API |
| Custom tolerances file upload | Not present | Optional tolerance file support | `tolerances_file_path` in verification execute request | Implemented in API |
| Log level selector | Not present | Log level dropdown | `log_level` in verification execute request | Implemented in API |
| Run verification action | Partial (`/run` executes workflow only) | Run verification from UI via REST | `POST /ai/verification/execute` | Implemented in API |
| Verification output logs display | Not present | Expandable stdout/stderr/log-like output sections | API response should include more execution details in next iteration | Planned |
| Summary report generation | Not present | Optional post-run summary generation | `generate_summary`, `summary_file_name`, `report_item_names` | Implemented in API |
| Render summary markdown | Not present | Render returned summary file content safely | Read endpoint for summary/report artifacts (next step) | Planned |
| Download ZIP of results | Not present | Download generated artifacts directly | Artifact listing/download endpoints (next step) | Planned |
| Chat assistant helper text | Not present | Keep simple guided helper, but tied to actual backend run state | Frontend-only UX, no API dependency | Planned |

## Immediate Build Backlog (Phase C -> D)

1. Add unified web UI page for verification execution that calls `POST /ai/verification/execute`.
2. Add artifact APIs for listing and downloading result files from run output directories.
3. Extend execution response shape to include command-like logs and warnings where available.
4. Add integration tests for verification execute endpoint (success, validation error, bad input paths).
5. Add frontend parity checks for required upload gating and advanced options behavior.

## Notes

- Current Streamlit app is coupled to Docker CLI orchestration; unified frontend target must call backend APIs only.
- Desktop PyQt remains fallback and should not become the primary path for new verification UX features.
