import sys
import warnings

sys.path.append("./constrain")

from constrain.api import Workflow

warnings.simplefilter(action="ignore", category=FutureWarning)
warnings.simplefilter(action="ignore", category=ResourceWarning)
workflow = Workflow(workflow="./examples/brick_demo/brick_workflow.json")
workflow.run_workflow(verbose=True)
