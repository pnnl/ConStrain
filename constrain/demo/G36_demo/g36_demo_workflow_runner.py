# %% [markdown]
# This demo showcases the usage of running a complete ConStrain verification process with a composed ConStrain workflow json file.
#
# Below is the runner code for running a multi-step verification process defined in `g36_demo_workflow.json`. This verification process runs 3 verification cases on a Modelica simulation dataset.
#
# Notes:
# - Users shall have all dependencies required by ConStrain installed to run this script:
#   - The project uses `poetry` to manage its dependencies, install it following the official installation instructions
#   - In the root folder run `poetry install`

# %%
import warnings
import sys, os

try:
    # works in scripts
    base_path = os.path.dirname(__file__)
except NameError:
    # fallback for notebooks
    base_path = os.getcwd()

# Change dir to align with workflow json file verification specification
os.chdir(os.path.join(base_path, "..", ".."))
# Insert the root directory at the beginning of sys.path to prioritize local constrain package
sys.path.insert(0, os.path.join('..'))

from constrain.api import Workflow

# %%
warnings.simplefilter(action="ignore", category=FutureWarning)
warnings.simplefilter(action="ignore", category=ResourceWarning)
workflow = Workflow(workflow="./demo/G36_demo/G36_demo_workflow.json")
workflow.run_workflow(verbose=True)
