import sys
import warnings

sys.path.append("./constrain")
from api import Workflow

warnings.simplefilter(action="ignore", category=FutureWarning)
warnings.simplefilter(action="ignore", category=ResourceWarning)
workflow = Workflow(workflow="./demo/hpwh_demo/hpwh_demo_workflow.json")
workflow.run_workflow(verbose=True)
