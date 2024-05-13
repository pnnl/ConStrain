import sys
import warnings

sys.path.append("./")

import constrain as cs

warnings.simplefilter(action="ignore", category=FutureWarning)
warnings.simplefilter(action="ignore", category=ResourceWarning)
workflow = cs.api.Workflow(workflow="./examples/brick_demo/brick_workflow.json")
workflow.run_workflow(verbose=True)
