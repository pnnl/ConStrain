import warnings
import sys, os

try:
    # works in scripts
    base_path = os.path.dirname(__file__)
except NameError:
    # fallback for notebooks
    base_path = os.getcwd()

# Insert the root directory at the beginning of sys.path to prioritize local constrain package
# sys.path.insert(0, os.path.join(base_path, "..", "..", ".."))
os.chdir(os.path.join(base_path, "..", ".."))
print(os.getcwd())
sys.path.insert(0, os.path.join('..'))
import constrain
from constrain.api import Workflow, WorkflowEngine


warnings.simplefilter(action="ignore", category=FutureWarning)
warnings.simplefilter(action="ignore", category=ResourceWarning)
workflow = Workflow(workflow="./demo/G36_demo/G36_demo_workflow.json")
workflow.run_workflow(verbose=True)
