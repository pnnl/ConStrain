# user_io

Host-shared input/output folder for Docker runs.

## Directory Structure

- Container mount root: `/user_io`

### User Input/Output (Your Own Files)
- **Host path**: `user_io/input/` and `user_io/output/`
- **Container paths**: `/user_io/input/...` and `/user_io/output/...`
- Use these directories for your own datasets and verification results.

### Example Input/Output (Sample Data)
- **Host path**: `user_io/examples/input/` and `user_io/examples/output/`
- **Container paths**: `/user_io/examples/input/...` and `/user_io/examples/output/...`
- When using `docker/docker-compose.yml`, existing sample data from `docker/examples` and `docker/examples_results` is automatically mounted here.

## Usage

Place your own datasets, case files, and other inputs under `user_io/input/` and reference them in forms as `/user_io/input/...`.

Verification outputs will be written to `/user_io/output/<run-name>` or another path you specify.
