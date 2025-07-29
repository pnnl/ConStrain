import warnings
import unittest
import sys
import os

# Add the project root to the path so we can import constrain
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from constrain.api import Workflow


class TestWorkflow(unittest.TestCase):
    def test_run_workflow(self):
        warnings.simplefilter(action="ignore", category=FutureWarning)
        warnings.simplefilter(action="ignore", category=ResourceWarning)
        workflow = Workflow(workflow="./constrain/demo/api_demo/demo_workflow.json")
        workflow.run_workflow(verbose=True)


if __name__ == "__main__":
    unittest.main()
