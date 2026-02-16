# Docker Configuration for ConStrain

This directory contains all Docker-related files for running ConStrain workflows and verification cases in containers.

## Files in this Directory

### Dockerfiles

- **Dockerfile.workflow** - Container for running workflow JSON files via the Workflow API
- **Dockerfile.verification** - Container for running verification case JSON files via the Verification API
- **Dockerfile.reporting** - Container for generating summary reports from verification results

### Configuration Files

- **.dockerignore** - Specifies files to exclude from Docker build context

## Quick Start

### Build Images

From project root

```bash
docker build -f docker/Dockerfile.workflow -t constrain:latest .
docker build -f docker/Dockerfile.verification -t constrain-verification:latest .
docker build -f docker/Dockerfile.reporting -t constrain-reporting:latest .
```

## Documentation

For detailed usage instructions, see:

- **Workflow Container**: [DOCKER_WORKFLOW.md](./DOCKER_WORKFLOW.md)
- **Verification Container**: [DOCKER_VERIFICATION.md](./DOCKER_VERIFICATION.md)
- **Reporting Container**: [DOCKER_REPORTING.md](./DOCKER_REPORTING.md)

## Additional Resources

- [ConStrain Documentation](https://pnnl.github.io/ConStrain/)
- [Workflow API Guide](https://pnnl.github.io/ConStrain/api/workflow.html)
- [Verification API Guide](https://pnnl.github.io/ConStrain/api/verification.html)
