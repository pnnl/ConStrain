import unittest, sys, logging, json, os
from unittest.mock import patch

import constrain
from constrain.api import Workflow

sys.path.append("./constrain")


class TestFlexibleCalling(unittest.TestCase):
    def test_no_dir_provided(self):
        """This test checks when no working directory is provided,
        if the program will behave correctly"""
        with self.assertLogs() as logobs:
            json_case_path = "./tests/api/data/verification_case_unit_test/verification_case_unit_test_Path.json"

            # Delete working_dir value in the json file
            with open(json_case_path, "r") as f:
                workflow_dict = json.load(f)
                del workflow_dict["working_dir"]

            with open(json_case_path, "w") as f:
                json.dump(workflow_dict, f)

            workflow = Workflow(workflow=json_case_path)
            self.assertEqual(
                logobs.output[0],
                "INFO:root:No working_dic is specified",
            )

    def test_invalid_str(self):
        """This test checks when working directory is not a valid string,
        if the program will behave correctly"""
        with self.assertLogs() as logobs:
            json_case_path = "./tests/api/data/verification_case_unit_test/verification_case_unit_test_Path.json"

            # Change working_dir value in the json file to a invalid string
            with open(json_case_path, "r") as f:
                workflow_dict = json.load(f)
                workflow_dict["working_dir"] = []

            with open(json_case_path, "w") as f:
                json.dump(workflow_dict, f)

            workflow = Workflow(workflow=json_case_path)
            self.assertEqual(
                logobs.output[0],
                "ERROR:root:working directory specified is not a valid string.",
            )



    def test_dir_not_exist(self):
        """This test checks when a valid wd is provided but it doesn't exist,
        if the program will behave correctly"""
        with self.assertLogs() as logobs:
            json_case_path = "./tests/api/data/verification_case_unit_test/verification_case_unit_test_Path.json"

            # Change working_dir value in the json file to a path that does not exist
            with open(json_case_path, "r") as f:
                workflow_dict = json.load(f)
                workflow_dict["working_dir"] = "./not_existing_path/test"

            with open(json_case_path, "w") as f:
                json.dump(workflow_dict, f)

            workflow = Workflow(workflow=json_case_path)
            self.assertEqual(
                logobs.output[1],
                "ERROR:root:working directory specified does not exist.",
            )


    """
    1. Probably another test is needed to check if the program can successfully detect if the WD provided is Linux format or Window format. 
    """


if __name__ == "__main__":
    unittest.main()
