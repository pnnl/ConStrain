import warnings
import sys
import constrain

from constrain.api import Workflow

warnings.simplefilter(action="ignore", category=FutureWarning)
warnings.simplefilter(action="ignore", category=ResourceWarning)
workflow = Workflow(workflow="./demo/G36_demo/G36_demo_workflow.json")
workflow.run_workflow(verbose=True)
