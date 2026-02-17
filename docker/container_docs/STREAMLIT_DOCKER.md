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
- Individual case reports
- Plots and visualizations

## Docker Compose Configuration

The `docker-compose.yml` includes the Streamlit service:

```yaml
streamlit:
  build:
    context: .
    dockerfile: Dockerfile.streamlit
  image: constrain-streamlit:latest
  container_name: constrain-streamlit
  ports:
    - "8501:8501"
  volumes:
    - /var/run/docker.sock:/var/run/docker.sock
  networks:
    - constrain-network
```

### Key Configuration Details:

- **Port 8501**: Streamlit's default port, mapped to host
- **Docker Socket Mount**: Allows spawning sibling containers
- **Network**: Connected to `constrain-network` for inter-container communication

## Building the Images

### Build All Services

```bash
cd docker
docker-compose build
```

### Build Only Streamlit

```bash
cd docker
docker-compose build streamlit
```

### Build Prerequisites

The Streamlit service depends on these images:
```bash
docker-compose build verification  # Required for running verifications
docker-compose build reporting     # Required for generating reports
```

## Advanced Usage

### Run with Custom Port

```bash
cd docker
docker-compose up streamlit -p 8502:8501
```

Then access at http://localhost:8502

### View Logs

```bash
docker-compose logs -f streamlit
```

### Restart Service

```bash
docker-compose restart streamlit
```

### Rebuild and Restart

```bash
docker-compose up -d --build streamlit
```

## Development

### Modify the Streamlit App

1. Edit `docker/streamlit_app.py`
2. Rebuild the image:
   ```bash
   cd docker
   docker-compose build streamlit
   ```
3. Restart the service:
   ```bash
   docker-compose up -d streamlit
   ```

### Debug Mode

Run in foreground to see logs:
```bash
cd docker
docker-compose up streamlit
```

### Shell Access

Get a shell inside the running container:
```bash
docker exec -it constrain-streamlit /bin/bash
```
