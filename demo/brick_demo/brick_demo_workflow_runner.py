import sys
import warnings

sys.path.append("./src")

from api import Workflow

warnings.simplefilter(action="ignore", category=FutureWarning)
warnings.simplefilter(action="ignore", category=ResourceWarning)
workflow = Workflow(workflow="./demo/brick_demo/brick_workflow.json")
workflow.run_workflow(verbose=True)
