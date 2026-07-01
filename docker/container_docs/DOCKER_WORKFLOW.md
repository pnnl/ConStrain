# Docker Setup for ConStrain Workflow API

This guide explains how to run ConStrain workflows using the workflow Docker container

## Prerequisites

- Docker installed on your system
- Workflow file in JSON format

## Quick Start

### Building the Docker Image

From project root:

```bash
docker build -f docker/Dockerfile.workflow -t constrain-workflow:latest .
```

### Running the Demo Workflow

The simplest way to test the container:

```bash
docker run --rm constrain-workflow:latest
```

This runs the default demo workflow located at `./constrain/demo/G36_demo/G36_demo_workflow.json`.

### Available Options

- `workflow_path` (optional): Path to the workflow JSON file. If not provided, uses default demo workflow
- `--log-level`: Logging level - choices: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` (default: `INFO`)

## Running Custom Workflows

### Using Docker Run with Volume Mounts

Mount your workflow JSON file and run it by passing the path as an argument:

```bash
docker run --rm \
  -v $(pwd)/docker/examples/workflows:/app/workflows \
  -v $(pwd)/docker/examples/data:/app/data \
  -v $(pwd)/docker/examples/verification_cases:/app/verification_cases \
  -v $(pwd)/docker/examples/schema:/app/schema \
  -v $(pwd)/docker/examples_results:/app/results \
  constrain-workflow:latest \
  /app/workflows/my_workflow.json
```

## Directory Structure

The Docker container expects the following directory structure:

```
/app/
├── constrain/          # ConStrain source code
├── workflows/          # Your custom workflow JSON files (mounted)
├── data/               # Data directory (mounted)
├── verification_cases/ # Verification cases directory (mounted)
├── schema/             # Schema directory (mounted)
├── results/            # Output directory (mounted)
├── weather/            # Weather data files (mounted, read-only)
└── resources/          # Energy+ IDD files (mounted, read-only)
```

## Volume Mounts

When running workflows, you typically want to mount these directories:

- **./workflows** → `/app/workflows`: Place your workflow JSON files here
- **./data** → `/app/data`: Place your data files here
- **./verification_cases** → `/app/verification_cases`: Place your verification case files here
- **./schema** → `/app/schema`: Place the ConStrain schema information files here
- **./results** → `/app/results`: Workflow outputs will be saved here
- **./weather** → `/app/weather`: Weather data files (if needed by your workflow)
- **./resources** → `/app/resources`: EnergyPlus IDD files (if needed)

## Example

The following is an example of running a user-defined workflow:

```bash
docker run --rm \
  -v $(pwd)/docker/examples/workflows:/app/workflows \
  -v $(pwd)/docker/examples/data:/app/data \
  -v $(pwd)/docker/examples/verification_cases:/app/verification_cases \
  -v $(pwd)/docker/examples/schema:/app/schema \
  -v $(pwd)/docker/examples_results:/app/results \
  constrain-workflow:latest \
  /app/workflows/G36_demo_workflow.json
```

## Inspecting the Container

To explore the container filesystem:

```bash
docker run --rm -it --entrypoint /bin/bash constrain-workflow:latest
```

## Notes on Optimized Dependencies

**PyQt6 (GUI Framework)**: Excluded - not required for headless workflow execution. If you need GUI functionality, use constrain outside of Docker or modify the Dockerfile.

**NumPy/SciPy (Minimal builds)**: Installed without full BLAS/LAPACK linear algebra libraries. This provides significantly smaller images while maintaining core functionality. If you require heavy numerical computing with optimized BLAS operations, you may need to modify the Dockerfile to install with full BLAS support (e.g., OpenBLAS or MKL).

## Additional Resources

- [ConStrain Documentation](https://pnnl.github.io/ConStrain/)
- [Workflow API Guide](https://pnnl.github.io/ConStrain/api/workflow.html)
- [Docker Documentation](https://docs.docker.com/)
