# Instructions for packaging ConStrain package locally with Poetry

ConStrain can be made a pip-able Python package using `poetry`. Here's a quick guide to go about creating the package, installing it, and testing it.

## Install `poetry`
```
curl -sSL https://install.python-poetry.org | python3 -
```
## Build `constrain` using `poetry`
From the root of the repository:
```
poetry build
```
## Install the package
From the root of the repository:
```
pip install .\dist\constrain-0.3.1-py3-none-any.whl
```
## Testing the package on one of the example scripts
```
python .\demo\G36_demo\g36_demo_workflow_runner.py
```
Should output something similar to the following:
```
[...]
Running state 12: [Success] ... Congratulations! the demo workflow is executed with expected results and no error!
Done. -- [22:19:51]
Workflow done at 22:19:51, a total of 12 states were executed in 0:00:33.789468.
```
## Run tests locally
```
poetry run pytest tests
```