# Docker Setup for ConStrain Reporting

This guide explains how to run ConStrain reporting to generate summary reports from multiple verification case results using the reporting Docker container.

## Prerequisites

- Docker installed on your system
- Verification case results in JSON format (typically generated from running verification cases)

## Quick Start

### Building the Docker Image

From project root

```bash
docker build -f docker/Dockerfile.reporting -t constrain-reporting:latest .
```

### Running Reporting

#### Basic Usage

```bash
docker run --rm constrain-reporting:latest [verification_json] [OPTIONS]
```

#### Available Options

- `verification_json` (required): Path to verification result JSON files. Use wildcards for multiple files (e.g., `/app/results/*_md.json`)
- `--output`: Name of the output summary report file (default: `results.md`)
- `--items`: List of verification class names to include. If empty, all results are included
- `--format`: Output format (default: `markdown`). Currently only markdown is supported
- `--log-level`: Logging level - choices: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` (default: `INFO`)

## Running Reports on Verification Results

### Using Docker Run with Volume Mounts

Mount your results directory containing verification case result JSON files:

```bash
docker run --rm \
  -v $(pwd)/docker/results:/app/results \
  constrain-reporting:latest \
  "/app/results/*_md.json" \
  --output summary.md
```

## Directory Structure

The Docker container expects the following directory structure:

```
/app/
├── constrain/          # ConStrain source code
├── results/            # Results directory (mounted)
│   ├── *_md.json       # Verification result JSON files
│   ├── results.md      # Generated summary report
│   └── case-*.md       # Individual case reports
```

## Volume Mounts

When running reporting, you typically want to mount these directories:

- **./results** → `/app/results`: Contains verification result JSON files and where report outputs will be saved

## Examples

### Example 1: Basic Report Generation

Generate a summary report from all verification results in a directory:

```bash
docker run --rm \
  -v $(pwd)/docker/examples_results:/app/results \
  constrain-reporting:latest \
  "/app/results/*_md.json" \
  --output results.md
```

### Example 2: Custom Output File Name

Generate a report with a custom output file name:

```bash
docker run --rm \
  -v $(pwd)/docker/examples_results:/app/results \
  constrain-reporting:latest \
  "/app/results/*_md.json" \
  --output G36_summary_report.md
```

### Example 3: Using Debug Logging

Run reporting with debug-level logging to see detailed execution information:

```bash
docker build -f docker/Dockerfile.reporting -t constrain-reporting:latest .
```

Then run with debug logging:
```bash
docker run --rm \
  -v $(pwd)/docker/examples_results:/app/results \
  constrain-reporting:latest \
  "/app/results/*_md.json" \
  --output results.md \
  --log-level DEBUG
```

### Example 5: Complete Workflow - Verification + Reporting

Run verification cases first, then generate a summary report:

```bash
# Step 1: Run verification cases
docker run --rm \
  -v $(pwd)/docker/examples/verification_cases:/app/verification_cases \
  -v $(pwd)/docker/examples/data:/app/data \
  -v $(pwd)/docker/examples/schema:/app/schema \
  -v $(pwd)/docker/examples_results:/app/results \
  constrain-verification:latest \
  /app/verification_cases/G36_library_verification_cases.json

# Step 2: Generate summary report
docker run --rm \
  -v $(pwd)/docker/examples_results:/app/results \
  constrain-reporting:latest \
  "/app/results/*_md.json" \
  --output verification_summary.md
```

## Inspecting the Container

To explore the container filesystem:

```bash
docker run --rm -it --entrypoint /bin/bash constrain-reporting:latest
```

## Notes on Optimized Dependencies

**PyQt6 (GUI Framework)**: Excluded - not required for headless reporting execution. If you need GUI functionality, use ConStrain outside of Docker or modify the Dockerfile.

**Minimal Image Size**: This image is optimized for reporting execution only, excluding unnecessary dependencies like PyQt6 to reduce image size and improve performance.

## Additional Resources

- [ConStrain Documentation](https://pnnl.github.io/ConStrain/)
- [Reporting API Guide](https://pnnl.github.io/ConStrain/api/reporting.html)
- [Docker Documentation](https://docs.docker.com/)
