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
        old_cwd = os.getcwd()
        os.chdir(
            "./constrain/"
        )  # Change dir to align with workflow json file verification specification
        try:
            workflow = Workflow(workflow="./demo/G36_demo/G36_demo_workflow.json")
            workflow.run_workflow(verbose=True)
        finally:
            os.chdir(old_cwd)


if __name__ == "__main__":
    unittest.main()
