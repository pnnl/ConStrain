## ConStrain AI Workflow Composer – User Guide

This guide walks you through:

- Setting up a Python environment for ConStrain using `uv`.
- Configuring an LLM provider for the AI workflow composer.
- Starting the AI composer web API and simple UI.
- Using the AI agent to generate a workflow + verification cases similar to the G36 demo.
- Running the generated workflow with the ConStrain API.

**Related documentation:** For design and architecture details see [AI_Workflow_Composer_Design.md](AI_Workflow_Composer_Design.md). For a short overview and use-case summary (including diagrams suitable for slides) see [AI_Workflow_Composer_Overview.md](AI_Workflow_Composer_Overview.md).

This guide assumes you are working from the project root:

```bash
cd /path/to/ConStrain
```

---

## 1. Environment setup with `uv`

ConStrain is configured as a Poetry project in `pyproject.toml`, and we recommend using `uv` for dependency management and execution.

### 1.1 Create (or reuse) the virtual environment

If you do not already have a `.venv` for this repo:

```bash
uv venv
```

If a `.venv` already exists, `uv` will automatically pick it up; you do not need to recreate it.

### 1.2 Install ConStrain (editable) with all runtime dependencies

From the project root:

```bash
uv pip install -e .
```

This will:

- Build and install `constrain` in editable mode.
- Install core dependencies plus the AI web stack:
  - `fastapi`
  - `uvicorn`
  - `jinja2`
  - `python-multipart`

You can verify that the key packages are importable:

```bash
uv run python -c "import fastapi, uvicorn, jinja2, multipart"
```

If this command exits without errors, your environment is ready.

---

## 2. Configure the LLM provider

The AI workflow composer is model-provider-agnostic, but it expects an **OpenAI-compatible HTTP API** (or similar) that exposes a `/chat/completions` endpoint.

The LLM client is configured via environment variables:

- `CONSTRAIN_LLM_API_BASE` – Base URL for the LLM endpoint  
  - Example (OpenAI-style): `https://api.openai.com/v1`
  - Example (self-hosted gateway): `https://my-llm-gateway.example.com/v1`
- `CONSTRAIN_LLM_MODEL` – Model name to use (e.g. `gpt-4.1-mini`, `gpt-4.1`, or a custom model ID).
- `CONSTRAIN_LLM_API_KEY` – API key or token (if required by your provider).
- `CONSTRAIN_LLM_TIMEOUT` (optional) – Request timeout in seconds (default: `30.0`).

Set these before starting any server:

```bash
export CONSTRAIN_LLM_API_BASE="https://api.openai.com/v1"
export CONSTRAIN_LLM_MODEL="gpt-4.1-mini"
export CONSTRAIN_LLM_API_KEY="YOUR_API_KEY_HERE"
```

If `CONSTRAIN_LLM_API_BASE` or `CONSTRAIN_LLM_MODEL` are missing, AI endpoints will report that no LLM is configured.

---

## 3. Starting the AI workflow services

There are two main entry points:

- A **REST API** for programmatic access.
- A **simple web UI** for interactive use in a browser.

Both live under the `constrain.app` package.

### 3.1 Start the REST API server

Run this from the project root:

```bash
uv run uvicorn constrain.app.ai_workflow_server:app --reload --host 127.0.0.1 --port 8000
```

Key endpoints (default base: `http://127.0.0.1:8000`):

- `POST /ai/workflow/suggest`
  - Input: JSON with `goal_description`, optional `data_context`, `existing_workflow`, `cases_context`.
  - Output: Suggested workflow JSON, validation status, and raw LLM text.
- `POST /ai/cases/suggest`
  - Input: JSON with `goal_description`, optional `signals_available`, `existing_cases`.
  - Output: Suggested verification-case suite JSON, validation status, and raw LLM text.
- `POST /ai/workflow/validate`
  - Input: `{ "workflow": { ... } }`
  - Output: Structural validation of a workflow definition.
- `POST /ai/cases/validate`
  - Input: `{ "cases": { "cases": [ ... ] } }`
  - Output: Structural validation of a verification-case suite.
- `GET /ai/catalog`
  - Output: Catalog of available callables and verification classes discovered via introspection.
- `POST /ai/workflow/execute`
  - Input: `{ "workflow": { ... }, "save_path": "..." }`
  - Output: Synchronous workflow execution result.
- `POST /ai/workflow/jobs`
  - Input: `{ "workflow": { ... }, "save_path": "..." }`
  - Output: Asynchronous workflow job handle (`job_id`) for polling.
- `POST /ai/verification/execute`
  - Input: verification payload (case file, output dir, plotting/report options).
  - Output: Synchronous verification/reporting result.
- `POST /ai/verification/jobs`
  - Input: same verification payload as `/ai/verification/execute`.
  - Output: Asynchronous verification job handle (`job_id`) for polling.
- `GET /ai/jobs/{job_id}`
  - Output: Job status and result metadata (`queued/running/succeeded/failed`).
- `GET /ai/artifacts/list`
  - Input: `output_dir` and optional `recursive`.
  - Output: Generated artifact metadata.
- `GET /ai/artifacts/download`
  - Input: `output_dir` + `relative_path`.
  - Output: Direct file download.
- `GET /ai/artifacts/download-zip`
  - Input: `output_dir`.
  - Output: Zip of all artifacts under the output directory.

These endpoints are implemented in:

- `constrain/app/ai_workflow_server.py`
- `constrain/ai/workflow_composer.py`
- `constrain/ai/schema_utils.py`
- `constrain/ai/introspection.py`

### 3.2 Start the simple web UI

For a browser-based experience, start the UI server:

```bash
export CONSTRAIN_API_BASE_URL="http://127.0.0.1:8000"
export CONSTRAIN_PUBLIC_API_BASE_URL="http://127.0.0.1:8000"
uv run uvicorn constrain.app.ai_workflow_ui:app --reload --host 127.0.0.1 --port 8080
```

Then open:

```text
http://127.0.0.1:8080/
```

Run API and UI on different ports (8000 and 8080) so they can run simultaneously.

The UI is defined in:

- `constrain/app/ai_workflow_ui.py`
- `constrain/app/templates/ai_workflow_index.html`

---

## 4. Using the AI agent to generate a workflow and verification cases

This section walks through using the **web UI** to create a workflow and verification-case JSON similar to the G36 demo.

### 4.1 Prepare context from the G36 demo

The original Guideline 36 example uses:

- Verification cases:  
  `constrain/demo/G36_demo/data/G36_library_verification_cases.json`
- Workflow definition:  
  `constrain/demo/G36_demo/G36_demo_workflow.json`
- Runner script:  
  `constrain/demo/G36_demo/g36_demo_workflow_runner.py`

These show a canonical pattern:

1. Load and preprocess data.
2. Load verification cases from JSON.
3. Validate cases and data.
4. Instantiate a `Verification` object and configure the run.
5. Execute verification.
6. Check that result files were produced.
7. Run reporting.

The AI agent will propose new JSONs following the same structure but tailored to your description.

### 4.2 Describe your goal in the UI

With `constrain.app.ai_workflow_ui` running:

1. Navigate to `http://127.0.0.1:8080/`.
2. In the **Goal** text area, describe what you want, for example:

   ```text
   I have a January dataset similar to the G36 demo at ./demo/G36_demo/data/G36_Modelica_Jan.csv.
   Please create a workflow and verification-case suite that:
   - Verifies G36 supply air temperature setpoint behavior,
   - Checks outdoor and return air damper positions,
   - Uses the standard ConStrain verification library.
   ```

3. (Optional) In **Data context (JSON)**, you can add specifics:

   ```json
   {
     "data_path": "./demo/G36_demo/data/G36_Modelica_Jan.csv",
     "data_source": "EnergyPlus"
   }
   ```

4. (Optional) In **Available signals (JSON)**, describe your signal mapping:

   ```json
   {
     "dev_settings": {
       "temperature_air_outdoor": "oa_t",
       "temperature_air_supply_setpoint": "sa_t_sp_ac"
     }
   }
   ```

5. Leave **Existing workflow JSON** and **Existing cases JSON** empty for a first-time generation (you can paste JSON here later for refinements).
6. Click **“Generate workflow & cases”**.

The UI will call:

- `suggest_workflow(...)` and
- `suggest_verification_cases(...)`

behind the scenes and show:

- **Workflow JSON** – a complete workflow definition.
- **Verification cases JSON** – a `{ "cases": [ ... ] }` suite.
- **Validation** sections for both, based on:
  - `constrain/schema/workflow.schema.json`
  - `VerificationCase.validate_verification_case_structure(...)`

### 4.3 Inspect and refine the AI output

In the right-hand panel:

- Review the **Workflow JSON**:
  - Check the `workflow_name`, `meta`, and `imports`.
  - Confirm that states follow a sensible sequence:
    - `load data`
    - `validate data`
    - `load verification cases`
    - `validate cases`
    - `setup verification`
    - `configure verification runner`
    - `run verification`
    - `check results`
    - `reporting`
  - Ensure `MethodCall` strings reference valid callables such as:
    - `DataProcessing`
    - `VerificationCase`
    - `Verification`
    - `Reporting`

- Review the **Verification cases JSON**:
  - Ensure each case has the required keys:
    - `no`, `run_simulation`, `simulation_IO.output`, `expected_result`,
      `datapoints_source.parameters`, `verification_class`.
  - Confirm `verification_class` names match items in the ConStrain library
    (e.g., `G36SupplyAirTemperatureSetpoint`, `G36OutdoorAirDamperPositionForReliefDamperOrFan`).

If validation issues appear, they are listed under **Validation** with:

- A path (`loc`) showing where the problem is.
- A message describing the issue.

You can:

- Copy the JSON to a local editor, fix issues, and paste it back into the **Existing workflow JSON** or **Existing cases JSON** fields.
- Adjust the **Goal** description and regenerate to nudge the AI toward the structure you want.

---

## 5. Saving and running the generated workflow

Once you are satisfied with the AI-generated workflow and cases:

### 5.1 Run the generated workflow from the UI or API

**From the web UI**

1. After generating (or pasting) a workflow in the **Workflow JSON** panel, click **Run workflow**.
2. The server validates the JSON, runs it with the ConStrain API, and re-renders the page.
3. Under **Execution** you will see either:
   - *Workflow executed successfully* and the number of states executed, or
   - An error message (e.g. invalid JSON, validation failure, or runtime exception).
4. The workflow runs in the same process as the UI; paths in the workflow (e.g. `data_path`, `json_case_path`, `output_path`) are relative to the server’s current working directory (usually the project root when you start `uvicorn` from there).

**From the REST API**

With the API server running (`uv run uvicorn constrain.app.ai_workflow_server:app --reload`), you can execute a workflow without the UI:

```bash
curl -X POST http://127.0.0.1:8000/ai/workflow/execute \
  -H "Content-Type: application/json" \
  -d '{
    "workflow": { ... your workflow JSON ... },
    "save_path": "./demo/ai_runs/ai_workflow.json"
  }'
```

- If the workflow is invalid, the API returns `400` with validation issues.
- If valid, it runs the workflow and returns `200` with `success`, `execution.summary` (e.g. `total_states_executed`, `state_running_sequence`), and optionally `execution.saved_to` when `save_path` is provided.

**From the command line (after saving JSON)**

Save the workflow and cases to files (see 5.3), then run via the ConStrain API, for example:

```bash
uv run python -c "from constrain.api import Workflow; Workflow('./demo/ai_runs/ai_workflow.json').run_workflow(verbose=True)"
```

### 5.2 Run verification from the UI (current behavior)

The verification form in the web UI (`POST /verify`) currently uses synchronous execution via:

- `POST /ai/verification/execute`

Behavior to expect:

- The request blocks until verification/reporting finishes (or fails).
- After completion, the UI immediately calls:
  - `GET /ai/artifacts/list`
- The page then renders artifact links and summary status.

Concurrency model (current implementation):

- Users are expected to submit one verification request at a time.
- Submitting a new verification while one is still running is not a supported usage pattern.

### 5.3 Save the JSON files

Copy the **Workflow JSON** from the UI and save it to a file, for example:

```bash
constrain/demo/my_demo/my_workflow.json
```

Copy the **Verification cases JSON** and save it similarly:

```bash
constrain/demo/my_demo/my_verification_cases.json
```

Make sure the paths inside the workflow (e.g., `data_path`, `json_case_path`, `output_path`) are relative to where you will run the workflow from (typically the project root).

### 5.4 Create a small runner script

Create a Python script (for instance, `constrain/demo/my_demo/run_my_workflow.py`) similar to the existing G36 runner:

```python
from constrain.api import Workflow


def main():
    workflow = Workflow(workflow="./demo/my_demo/my_workflow.json")
    workflow.run_workflow(verbose=True)


if __name__ == "__main__":
    main()
```

Run it via `uv`:

```bash
uv run python constrain/demo/my_demo/run_my_workflow.py
```

This will:

- Load and validate your workflow JSON.
- Execute the states in sequence.
- Produce verification result files (typically `*_md.json`) and reports, depending on how the workflow is configured.

### 5.5 Verifying outputs

After the run completes:

- Look for `*_md.json` result files in your configured `output_path`.
- If your workflow includes reporting states, there may be:
  - Summary markdown files (e.g., `report_summary.md`).
  - Per-case detailed markdown reports.

You can adapt the reporting configuration from the G36 demo if you want similar artifacts.

---

## 6. Programmatic use of the AI API (optional)

If you prefer not to use the browser UI, you can call the AI API directly (with the `ai_workflow_server` running).

Example (using `curl`) for workflow suggestion:

```bash
curl -X POST http://127.0.0.1:8000/ai/workflow/suggest \
  -H "Content-Type: application/json" \
  -d '{
    "goal_description": "Generate a workflow similar to the G36 demo using my January dataset.",
    "data_context": {
      "data_path": "./demo/G36_demo/data/G36_Modelica_Jan.csv",
      "data_source": "EnergyPlus"
    }
  }'
```

Example for verification-case suggestion:

```bash
curl -X POST http://127.0.0.1:8000/ai/cases/suggest \
  -H "Content-Type: application/json" \
  -d '{
    "goal_description": "Create G36 supply air temperature and damper-related verification cases."
  }'
```

You can then save `workflow` and `cases` from the responses to JSON files and run them as described in Section 5.

Example for synchronous verification execution:

```bash
curl -X POST http://127.0.0.1:8000/ai/verification/execute \
  -H "Content-Type: application/json" \
  -d '{
    "case_file_path": "./docker/examples/verification_cases/G36_library_verification_cases.json",
    "output_dir": "./docker/examples_results/manual_run",
    "data_file_path": "./docker/examples/data/G36_Modelica_Jan.csv",
    "library_json_path": "./docker/examples/schema/library.json",
    "plot_option": "all-compact",
    "fig_size": [6.4, 4.8],
    "log_level": "INFO",
    "generate_summary": true,
    "summary_file_name": "verification_summary.md"
  }'
```

Example for listing and downloading artifacts:

```bash
curl "http://127.0.0.1:8000/ai/artifacts/list?output_dir=./docker/examples_results/manual_run&recursive=true"
curl -L -o verification_summary.md "http://127.0.0.1:8000/ai/artifacts/download?output_dir=./docker/examples_results/manual_run&relative_path=verification_summary.md"
curl -L -o verification_results.zip "http://127.0.0.1:8000/ai/artifacts/download-zip?output_dir=./docker/examples_results/manual_run"
```

---

## 7. Troubleshooting

- **No LLM configured / 503 errors on /ai/* endpoints**
  - Ensure `CONSTRAIN_LLM_API_BASE` and `CONSTRAIN_LLM_MODEL` are set.
  - Verify network access from the machine running ConStrain to your LLM endpoint.

- **Import errors for FastAPI/uvicorn/Jinja2**
  - Re-run:

    ```bash
    uv pip install -e .
    uv run python -c "import fastapi, uvicorn, jinja2, multipart"
    ```

  - Confirm you are running commands *inside* the ConStrain project directory.

- **Workflow or cases marked invalid in the UI**
  - Inspect the validation issues displayed under each JSON panel.
  - Pay attention to:
    - Missing required keys.
    - Wrong types (e.g., string instead of number).
    - Invalid or unknown `verification_class` names.
  - Edit and revalidate until the issues list is empty.

- **API and UI cannot both start on port 8000**
  - Start API on `127.0.0.1:8000` and UI on `127.0.0.1:8080`.
  - Set `CONSTRAIN_API_BASE_URL` and `CONSTRAIN_PUBLIC_API_BASE_URL` before launching the UI.

With this setup, you can iteratively design, validate, and execute ConStrain workflows using the AI agent, leveraging both the existing verification library and your own datasets.
