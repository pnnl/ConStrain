import warnings

import unittest, sys, datetime, copy

sys.path.append("./constrain")

from api import Workflow


class TestWorkflow(unittest.TestCase):
    def test_run_workflow(self):
        warnings.simplefilter(action="ignore", category=FutureWarning)
        warnings.simplefilter(action="ignore", category=ResourceWarning)
        workflow = Workflow(workflow="./demo/api_demo/demo_workflow.json")
        workflow.run_workflow(verbose=True)


if __name__ == "__main__":
    unittest.main()
