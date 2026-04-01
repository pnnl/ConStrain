# user_io

Host-shared input/output folder for Docker runs.

- Container mount root: `/user_io`
- Example input paths: `/user_io/examples/input/...`
- Example output paths: `/user_io/examples/output/...`

Place user-provided datasets and verification assets under this folder when running Docker services.

When using `docker/docker-compose.yml`, existing sample data from `docker/examples` and `docker/examples_results` is mounted into:

- `/user_io/examples/input`
- `/user_io/examples/output`
