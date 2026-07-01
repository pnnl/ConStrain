# ConStrain – Docker Quick Start Guide

This guide covers starting the full ConStrain stack with Docker Compose and using it from the browser.

---

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (or Docker Engine + Compose plugin) installed and running.
- The repository cloned locally.

---

## 1. Start the stack

Run from the **repository root**:

```bash
docker compose -f docker/docker-compose.yml up -d --build
```

This builds and starts two containers:

| Container | Host port | Description |
|---|---|---|
| `constrain-api-server` | **8000** | Backend REST API (verification, workflow execution, artifacts) |
| `constrain-api-ui` | **8080** | Web UI (browser interface) |

Verify both services are healthy:

```bash
docker compose -f docker/docker-compose.yml ps
```

Both should show `(healthy)` within ~30 seconds.

---

## 2. Open the web interface

Navigate to **[http://localhost:8080](http://localhost:8080)** in your browser.

You will see the home page with two sections:

- **Workflow Composer** – Describe your verification goals in natural language; the AI generates workflow and verification-case JSON.
- **Verification Execution** – Run existing verification case files directly, view results, and download artifacts.

---

## 3. Generate a workflow with the AI composer

1. Go to [http://localhost:8080/workflow](http://localhost:8080/workflow).
2. In the **Goal** box, describe what you want, for example:
   ```
   Verify G36 supply air temperature setpoint and outdoor air damper
   behavior using my January dataset.
   ```
3. Under **GenAI provider settings**, fill in your LLM credentials — no terminal export required:
   - **LLM API base URL** – e.g. `https://api.openai.com/v1`
   - **LLM model** – e.g. `gpt-4.1-mini`
   - **LLM API key** – your API key or token
4. Click **Generate workflow & cases**.
5. The AI proposals panel shows the generated **Workflow JSON** and **Verification cases JSON**, along with any validation issues.
6. Edit the JSON directly in the text area if needed, then click **Run workflow** to execute it.

> **Alternative:** If you prefer to set LLM credentials once for all requests, pass them as environment variables before starting the stack (see §5 below). The page-level fields are optional and take precedence when filled.

---

## 4. Run verification cases

1. Go to [http://localhost:8080/verification](http://localhost:8080/verification).
2. Fill in the form fields. Paths are resolved **inside the containers** — use the pre-mounted paths:

   | Field | Example value inside container |
   |---|---|
   | Case file path | `/data/verification_cases/G36_library_verification_cases.json` |
   | Output directory | `/data/results/my-run` |
   | Data file path | `/data/data/G36_Modelica_Jan.csv` |
   | Library JSON path | `/data/schema/library.json` |

3. Click **Run verification**.
4. When complete, a results section appears with a list of generated artifacts.
5. Click any artifact link to download it, or use the **Download all as zip** link.

---

## 5. Environment variable overrides (optional)

Create a file named `.env` inside the `docker/` subdirectory of the repository
(i.e. `<repo-root>/docker/.env`) to override defaults before starting the stack.
Docker Compose reads this file automatically when you run commands from that directory.
This is useful for pre-configuring an LLM provider so every page request inherits it automatically:

```bash
# Create/edit the file from the repository root:
# nano docker/.env    (or any editor)

# docker/.env contents:
LOG_LEVEL=INFO
CONSTRAIN_LLM_API_BASE=https://api.openai.com/v1
CONSTRAIN_LLM_MODEL=gpt-4.1-mini
CONSTRAIN_LLM_API_KEY=YOUR_API_KEY_HERE

# On Linux, match container UID/GID to your host user to avoid permission issues:
APP_UID=1000
APP_GID=1000
```

Then start the stack from the `docker/` directory:

```bash
cd docker && docker compose up -d --build
```

---

## 6. Stop the stack

```bash
docker compose -f docker/docker-compose.yml down
```

Results written to `docker/examples_results/` on the host persist after the stack is stopped.

---

## Troubleshooting

| Symptom | Check |
|---|---|
| Containers show `(unhealthy)` | Run `docker compose -f docker/docker-compose.yml logs api-server` to inspect startup errors. |
| `http://localhost:8080` not reachable | Confirm port 8080 is not blocked by another process (`lsof -i :8080`). |
| "No LLM client configured" error | Fill in the **GenAI provider settings** on the compose page, or set `CONSTRAIN_LLM_*` in `docker/.env` and rebuild. |
| Permission errors on results | Set `APP_UID`/`APP_GID` in `docker/.env` to match your host user (`id -u` / `id -g`). |

For more detail see [docker/TROUBLESHOOTING.md](../docker/TROUBLESHOOTING.md).

---

## Further reading

| Document | Purpose |
|---|---|
| [docs/Workflow_AI_User_Guide.md](Workflow_AI_User_Guide.md) | Full setup and step-by-step usage (local dev, API, CLI). |
| [docs/AI_Workflow_Composer_Overview.md](AI_Workflow_Composer_Overview.md) | High-level overview and architecture diagrams. |
| [docker/README.md](../docker/README.md) | Docker environment details and advanced overrides. |
