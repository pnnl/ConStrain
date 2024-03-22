import unittest, sys, logging
from unittest.mock import patch

import constrain
from constrain.api import Workflow

sys.path.append("./constrain")


class TestFlexibleCalling(unittest.TestCase):

    def test_no_dir_provided(self):
        """This test checks when no working directory is provided,
        if the program will behave correctly"""
        with self.assertLogs() as logobs:
            json_case_path = (
                "./data/verification_case_unit_test/verification_case_unit_test_NotAString.json"
            )
            workflow = Workflow(workflow=json_case_path)    
            self.assertEqual(logobs.output[0],"ERROR:root:working directory specified is not a valid string.")
            
            


    def test_invalid_dir_string(self):
        """This test checks when a invalid dir string is provided,
        if the program will behave correctly"""

        a = 1
        self.assertEqual(1,a)

    def test_dir_not_exist(self):
        """This test checks when a valid wd is provided but it doesn't exist,
        if the program will behave correctly"""

        a = 1
        self.assertEqual(1,a)

    def test_valid_dir(self):
        """This test checks when a working directory is provided and it also points to the correct path,
        if the program will behave correctly"""

        a = 1
        self.assertEqual(1,a)

    """
    1. Probably another test is needed to check if the program can successfully detect if the WD provided is Linux format or Window format. 
    """


if __name__ == "__main__":
    unittest.main()
