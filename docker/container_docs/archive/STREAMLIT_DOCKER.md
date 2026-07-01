# ConStrain Streamlit UI - Legacy Docker Deployment

This document is archived for historical reference.

Status:
- Deprecated fallback/reference only
- Not part of the supported API-first docker-compose runtime
- Replaced by `api-server` and `api-ui` in `docker/docker-compose.yml`

Reason for archival:
- The legacy Streamlit deployment relied on Docker socket access and sibling-container orchestration.
- The supported runtime now uses API-first execution through FastAPI services and removes the Docker socket exposure.

Historical content follows.

# ConStrain Streamlit UI - Docker Deployment

A containerized web interface for running ConStrain verification cases with automatic report generation.

## Quick Start

### 1. Build and Start the Service

```bash
cd docker
docker-compose up -d streamlit
```

### 2. Access the UI

Open your browser and navigate to:

```
http://localhost:8501
```

### 3. Stop the Service

```bash
docker-compose down streamlit
```

## Architecture

```
┌─────────────────────────────────────────────┐
│   Browser (http://localhost:8501)          │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│   Streamlit Container                       │
│   - Web UI running on port 8501             │
│   - Has access to Docker socket             │
└──────────────┬──────────────────────────────┘
               │
               │ Spawns containers via Docker socket
               ▼
┌─────────────────────────────────────────────┐
│   Sibling Containers                        │
│   - constrain-verification (runs checks)    │
│   - constrain-reporting (generates reports) │
└─────────────────────────────────────────────┘
```

## How It Works

1. **Streamlit runs in a Docker container** with access to the Docker socket (`/var/run/docker.sock`)
2. **Users upload files** through the web browser
3. **Files are saved** to temporary directories inside the container
4. **Verification container is spawned** as a sibling container with volume mounts
5. **Reporting container is spawned** to generate summary reports
6. **Results are displayed** in the UI with download buttons

## Usage

### Step 1: Upload Files

In the sidebar, upload three required files:

1. **Data CSV File**: Your simulation or measured data
2. **Verification Case JSON**: Defines what to verify
3. **ConStrain Library JSON**: Library of verification items

### Step 2: Run Verification

Click the **"Run Verification"** button and watch the progress:
- Verification runs
- Summary report is generated
- All files are available for download

### Step 3: Download Results

Download any generated files:
- Verification results (JSON)
- Summary reports (Markdown)