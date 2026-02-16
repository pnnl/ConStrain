# Docker Configuration for ConStrain

This directory contains all Docker-related files for running ConStrain workflows and verification cases in containers.

## Files in this Directory

### Dockerfiles

- **Dockerfile.workflow** - Container for running workflow JSON files via the Workflow API
- **Dockerfile.verification** - Container for running verification case JSON files via the Verification API
- **Dockerfile.reporting** - Container for generating summary reports from verification results

### Configuration Files

- **.dockerignore** - Specifies files to exclude from Docker build context

### Documentation

- **DOCKER.md** - Complete guide for using the workflow container
- **DOCKER_VERIFICATION.md** - Complete guide for using the verification container
- **DOCKER_REPORTING.md** - Complete guide for using the reporting container
- **IMAGE_SIZE_ANALYSIS.md** - Analysis of image size and optimization strategies
- **analyze_image_size.sh** - Script to analyze built image sizes

## Quick Start

### Build Images

```bash
# From project root
docker build -f docker/Dockerfile.workflow -t constrain:latest .
docker build -f docker/Dockerfile.verification -t constrain-verification:latest .
docker build -f docker/Dockerfile.reporting -t constrain-reporting:latest .
```

### Run Containers

```bash
# From project root
docker run --rm \
  -v $(pwd)/workflows:/app/workflows \
  -v $(pwd)/results:/app/results \
  constrain:latest \
  /app/workflows/my_workflow.json

docker run --rm \
  -v $(pwd)/workflows:/app/workflows \
  -v $(pwd)/results:/app/results \
  constrain-verification:latest \
  /app/workflows/case.json

docker run --rm \
  -v $(pwd)/results:/app/results \
  constrain-reporting:latest \
  "/app/results/*_md.json" --output results.md
```

## Image Specifications

Both containers share the same optimizations:

- **Base**: python:3.10-slim
- **Size**: ~0.9-1.2GB (optimized)
- **Optimizations**:
  - Multi-stage build
  - PyQt6 excluded (~30-50MB saved)
  - Minimal numpy/scipy builds (~50-100MB saved)
  - Comprehensive .dockerignore (~80% of files excluded)

## Documentation

For detailed usage instructions, see:

- **Workflow Container**: [DOCKER.md](./DOCKER.md)
- **Verification Container**: [DOCKER_VERIFICATION.md](./DOCKER_VERIFICATION.md)
- **Reporting Container**: [DOCKER_REPORTING.md](./DOCKER_REPORTING.md)
- **Size Analysis**: [IMAGE_SIZE_ANALYSIS.md](./IMAGE_SIZE_ANALYSIS.md)

## Container Comparison

| Feature | Workflow | Verification | Reporting |
|---------|----------|--------------|-----------|
| Dockerfile | Dockerfile.workflow | Dockerfile.verification | Dockerfile.reporting |
| Entrypoint | docker/run_workflow.py | docker/run_verification.py | docker/run_reporting.py |
| Primary use | Execute workflows | Run verifications | Aggregate results |
| Input format | Workflow state machine | Verification case JSON | Result JSON files |
| CLI arguments | Single file path | File path + options | Pattern + options |
| Image size | ~0.9-1.2GB | ~0.9-1.2GB | ~0.9-1.2GB |

## Directory Structure in Containers

```
/app/
├── constrain/          # ConStrain source code
├── run_workflow.py     # Workflow entrypoint (copied from docker/)
├── run_verification.py # Verification entrypoint (copied from docker/)
├── workflows/          # Mounted: your JSON files
├── results/            # Mounted: output directory
├── data/               # Mounted: input data (verification container)
├── resources/          # Included: EnergyPlus IDD files
└── schema/             # Included: library schemas
```

## Troubleshooting

### Build Issues

If you encounter build issues:

```bash
# Clean build without cache
docker build --no-cache -f docker/Dockerfile.workflow -t constrain:latest .

# Check .dockerignore is being used
docker build -f docker/Dockerfile.workflow -t constrain:latest . 2>&1 | grep "Sending build context"
```

### Permission Issues

If you get permission errors with volumes:

```bash
docker run --rm --user $(id -u):$(id -g) \
  -v $(pwd)/workflows:/app/workflows \
  -v $(pwd)/results:/app/results \
  constrain:latest /app/workflows/my_workflow.json
```

## Additional Resources

- [ConStrain Documentation](https://pnnl.github.io/ConStrain/)
- [Workflow API Guide](https://pnnl.github.io/ConStrain/api/workflow.html)
- [Verification API Guide](https://pnnl.github.io/ConStrain/api/verification.html)
- [Docker Documentation](https://docs.docker.com/)
