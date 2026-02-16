# Docker Setup for ConStrain Workflow API

This guide explains how to run ConStrain workflows using the workflow Docker container

## Prerequisites

- Docker installed on your system

## Quick Start

### Building the Docker Image

```bash
# From project root
docker build -f docker/Dockerfile.workflow -t constrain:latest .
```

### Running the Demo Workflow

The simplest way to test the container:

```bash
docker run --rm constrain:latest
```

This runs the default demo workflow located at `./constrain/demo/api_demo/demo_workflow.json`.

## Running Custom Workflows

### Using Docker Run with Volume Mounts

Mount your workflow JSON file and run it by passing the path as an argument:

```bash
docker run --rm \
  -v $(pwd)/workflows:/app/workflows \
  -v $(pwd)/results:/app/results \
  constrain:latest \
  /app/workflows/my_workflow.json
```

## Directory Structure

The Docker container expects the following directory structure:

```
/app/
├── constrain/          # ConStrain source code
├── workflows/          # Your custom workflow JSON files (mounted)
├── results/            # Output directory (mounted)
├── weather/            # Weather data files (mounted, read-only)
└── resources/          # Energy+ IDD files (mounted, read-only)
```

## Volume Mounts

When running workflows, you typically want to mount these directories:

- **./workflows** → `/app/workflows`: Place your workflow JSON files here
- **./results** → `/app/results`: Workflow outputs will be saved here
- **./weather** → `/app/weather`: Weather data files (if needed by your workflow)
- **./resources** → `/app/resources`: EnergyPlus IDD files (if needed)

## Example

The following is an example of running a user-defined workflow:

```bash
docker run --rm \
  -v $(pwd)/docker/examples:/app/workflows \
  -v $(pwd)/examples:/app/results \
  constrain:latest \
  /app/workflows/G36_demo_workflow.json
```

## Troubleshooting

### Viewing Logs

To see detailed logs with docker run:

```bash
docker run --rm constrain:latest 2>&1 | tee workflow.log
```

### Inspecting the Container

To explore the container filesystem:

```bash
docker run --rm -it --entrypoint /bin/bash constrain:latest
```

### Notes on Optimized Dependencies

**PyQt6 (GUI Framework)**: Excluded - not required for headless workflow execution. If you need GUI functionality, use constrain outside of Docker or modify the Dockerfile.

**NumPy/SciPy (Minimal builds)**: Installed without full BLAS/LAPACK linear algebra libraries. This provides significantly smaller images while maintaining core functionality. If you require heavy numerical computing with optimized BLAS operations, you may need to modify the Dockerfile to install with full BLAS support (e.g., OpenBLAS or MKL).

## Additional Resources

- [ConStrain Documentation](https://pnnl.github.io/ConStrain/)
- [Workflow API Guide](https://pnnl.github.io/ConStrain/api/workflow.html)
- [Docker Documentation](https://docs.docker.com/)
