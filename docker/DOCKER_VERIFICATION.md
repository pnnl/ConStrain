# Docker Setup for ConStrain Verification Cases

This guide explains how to run ConStrain verification cases using the verification Docker container.

## Prerequisites

- Docker installed on your system

## Quick Start

### Building the Docker Image

From project root

```bash
docker build -f docker/Dockerfile.verification -t constrain-verification:latest .
```

### Running a Verification Case

#### Basic Usage

```bash
docker run --rm constrain-verification:latest [case_file] [OPTIONS]
```

#### Available Options

- `case_file` (required): Path to the verification case JSON file
- `--output`: Output directory for verification results (default: `/app/results`)
- `--lib-items`: Path to library items JSON file (default: `./schema/library.json`)
- `--data`: Path to preprocessed data CSV file (optional)
- `--plot-option`: Type of plots to generate - choices: `all-compact`, `all-expand`, `day-compact`, `day-expand` (default: `all-compact`)
- `--fig-size`: Figure size as width,height (default: `6.4,4.8`)
- `--tolerances`: Path to custom tolerances JSON file (optional)

## Running Custom Verification Cases

### Using Docker Run with Volume Mounts

Mount your results and data folder that includes your verification case file and run it by passing the path as an argument:

```bash
docker run --rm \
  -v $(pwd)/docker/verifications:/app/data \
  -v $(pwd)/docker/results:/app/results \
  constrain-verification:latest \
  /app/workflows/verification_case.json
```

## Directory Structure

The Docker container expects the following directory structure:

```
/app/
├── constrain/          # ConStrain source code
├── data/               # Data directory (mounted)
├── verification_cases/ # Verification cases directory (mounted)
├── schema/             # Schema directory (mounted)
├── results/            # Output directory (mounted)
├── weather/            # Weather data files (mounted, read-only)
└── resources/          # Energy+ IDD files (mounted, read-only)
```

## Volume Mounts

When running verification cases, you typically want to mount these directories:

- **./data** → `/app/data`: Place your data files here
- **./verification_cases** → `/app/verification_cases`: Place your verification case files here
- **./schema** → `/app/schema`: Place the ConStrain schema information files here
- **./results** → `/app/results`: Workflow outputs will be saved here
- **./weather** → `/app/weather`: Weather data files (if needed by your workflow)
- **./resources** → `/app/resources`: EnergyPlus IDD files (if needed)

## Examples

### Example 1: Basic Verification

```bash
docker run --rm \
  -v $(pwd)/docker/examples/verification_cases:/app/verification_cases \
  -v $(pwd)/docker/examples/data:/app/data \
  -v $(pwd)/docker/examples/schema:/app/schema \
  -v $(pwd)/docker/examples_results:/app/results \
  constrain-verification:latest \
  /app/verification_cases/G36_library_verification_cases.json
```

### Example 2: Verification with All Options

```bash
docker run --rm \
  -v $(pwd)/docker/examples/verification_cases:/app/verification_cases \
  -v $(pwd)/docker/examples/data:/app/data \
  -v $(pwd)/docker/examples/schema:/app/schema \
  -v $(pwd)/docker/examples_results:/app/results \
  -v $(pwd)/constrain/tolerances.json:/app/tolerances.json \
  constrain-verification:latest \
  /app/verification_cases/G36_library_verification_cases.json \
  --output /app/results \
  --lib-items /app/schema/library.json \
  --data /app/data/G36_Modelica_Jan.csv \
  --plot-option all-expand \
  --fig-size 10,8 \
  --tolerances /app/tolerances.json
```

## Inspecting the Container

To explore the container filesystem:

```bash
docker run --rm -it --entrypoint /bin/bash constrain-verification:latest
```

## Notes on Optimized Dependencies

**PyQt6 (GUI Framework)**: Excluded - not required for headless verification execution. If you need GUI functionality, use ConStrain outside of Docker or modify the Dockerfile.

**Minimal Image Size**: This image is optimized for verification case execution only, excluding unnecessary dependencies like PyQt6 to reduce image size and improve performance.

## Additional Resources

- [ConStrain Documentation](https://pnnl.github.io/ConStrain/)
- [Verification API Guide](https://pnnl.github.io/ConStrain/api/verification.html)
- [Docker Documentation](https://docs.docker.com/)
