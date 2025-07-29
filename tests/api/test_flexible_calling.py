import unittest, sys, logging, json, os
import platform
from unittest.mock import patch

# Add the project root to the path so we can import constrain
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from constrain.api import Workflow


class TestFlexibleCalling(unittest.TestCase):
    def test_no_dir_provided(self):
        """This test checks when no working directory is provided,
        if the program will behave correctly"""
        with self.assertLogs() as logobs:
            json_case_path = "./tests/api/data/flexible_calling_unit_test/verification_case_unit_test_Path.json"

            # Delete working_dir value in the json file
            with open(json_case_path, "r") as f:
                workflow_dict = json.load(f)
                workflow_dict.pop("working_dir", None)

            with open(json_case_path, "w") as f:
                json.dump(workflow_dict, f)

            workflow = Workflow(workflow=json_case_path)
            self.assertEqual(
                logobs.output[0],
                "INFO:root:No working_dir is specified",
            )

    def test_invalid_str(self):
        """This test checks when working directory is not a valid string,
        if the program will behave correctly"""
        with self.assertLogs() as logobs:
            json_case_path = "./tests/api/data/flexible_calling_unit_test/verification_case_unit_test_Path.json"

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

    def test_Linux_path(self):
        """This test check if the program can detect the working path provided is in Linux format."""
        with self.assertLogs() as logobs:
            json_case_path = "./tests/api/data/flexible_calling_unit_test/verification_case_unit_test_Path.json"

            # Change working_dir value in the json file to a valid path in Linux format
            with open(json_case_path, "r") as f:
                workflow_dict = json.load(f)
                workflow_dict["working_dir"] = "./tests/api/result"

            with open(json_case_path, "w") as f:
                json.dump(workflow_dict, f)

            workflow = Workflow(workflow=json_case_path)

            current_dir = os.getcwd()

            # change current working directory back
            os.chdir("../../..")

            self.assertEqual(
                logobs.output[0],
                "INFO:root:the working dir provided is in Linux format.",
            )

            self.assertEqual(
                logobs.output[1],
                "INFO:root:Change current working path to the specified path.",
            )

            os.chdir(current_dir)

    def test_Win_path(self):
        """This test check if the program can detect the working path provided is in WIN format."""
        with self.assertLogs() as logobs:
            json_case_path = "./tests/api/data/flexible_calling_unit_test/verification_case_unit_test_Path.json"

            # Change working_dir value in the json file to a valid path in Win format
            with open(json_case_path, "r") as f:
                workflow_dict = json.load(f)
                workflow_dict["working_dir"] = ".\\tests\\api\\result"

            with open(json_case_path, "w") as f:
                json.dump(workflow_dict, f)

            workflow = Workflow(workflow=json_case_path)

            current_dir = os.getcwd()

            # change current working directory back
            os.chdir("../../..")

            self.assertEqual(
                logobs.output[0],
                "INFO:root:the working dir provided is in Win format.",
            )
            self.assertEqual(
                logobs.output[1],
                "INFO:root:Change current working path to the specified path.",
            )

            os.chdir(current_dir)

    def test_valid_dir(self):
        """This test checks when a working directory is provided and it also points to the correct path,
        if the program will behave correctly"""
        with self.assertLogs() as logobs:
            json_case_path = "./tests/api/data/flexible_calling_unit_test/verification_case_unit_test_Path.json"

            # Change working_dir value in the json file to a valid path
            with open(json_case_path, "r") as f:
                workflow_dict = json.load(f)
                workflow_dict["working_dir"] = "./tests/api/result"

            with open(json_case_path, "w") as f:
                json.dump(workflow_dict, f)

            workflow = Workflow(workflow=json_case_path)

            current_dir = os.getcwd()

            # change current working directory back
            os.chdir("../../..")

            self.assertEqual(
                logobs.output[1],
                "INFO:root:Change current working path to the specified path.",
            )

            os.chdir(current_dir)

        with self.assertLogs() as logobs:
            # Change working_dir value in the json file to a valid path in Win format
            with open(json_case_path, "r") as f:
                workflow_dict = json.load(f)
                workflow_dict["working_dir"] = ".\\tests\\api\\result"

            with open(json_case_path, "w") as f:
                json.dump(workflow_dict, f)

            workflow = Workflow(workflow=json_case_path)

            current_dir = os.getcwd()

            # Change current working directory back
            os.chdir("../../..")

            self.assertEqual(
                logobs.output[1],
                "INFO:root:Change current working path to the specified path.",
            )

            os.chdir(current_dir)

    def test_dir_with_space(self):
        """This test checks when a working directory with space is provided and it also points to the correct path,
        if the program will behave correctly"""
        with self.assertLogs() as logobs:
            json_case_path = "./tests/api/data/flexible_calling_unit_test/verification_case_unit_test_Path.json"

            # Change working_dir value in the json file to a valid path in Linux format with space
            with open(json_case_path, "r") as f:
                workflow_dict = json.load(f)
                workflow_dict["working_dir"] = "./tests/api/result/dir space"

            with open(json_case_path, "w") as f:
                json.dump(workflow_dict, f)

            workflow = Workflow(workflow=json_case_path)

            current_dir = os.getcwd()

            # change current working directory back
            os.chdir("../../../../")

            self.assertEqual(
                logobs.output[1],
                "INFO:root:Change current working path to the specified path.",
            )

            os.chdir(current_dir)

        with self.assertLogs() as logobs:
            # Change working_dir value in the json file to a valid path in Win format with space
            with open(json_case_path, "r") as f:
                workflow_dict = json.load(f)
                workflow_dict["working_dir"] = ".\\tests\\api\\result\\dir space"

            with open(json_case_path, "w") as f:
                json.dump(workflow_dict, f)

            workflow = Workflow(workflow=json_case_path)

            current_dir = os.getcwd()

            # Change current working directory back
            os.chdir("../../../../")

            self.assertEqual(
                logobs.output[1],
                "INFO:root:Change current working path to the specified path.",
            )

            os.chdir(current_dir)

    def test_dir_simple(self):
        """This test checks when a simple working directory without any "\\" or "/" is provided and it also points to the correct path,
        if the program will behave correctly"""
        with self.assertLogs() as logobs:
            json_case_path = "./tests/api/data/flexible_calling_unit_test/verification_case_unit_test_Path.json"

            # Change working_dir value in the json file to a valid path
            with open(json_case_path, "r") as f:
                workflow_dict = json.load(f)
                workflow_dict["working_dir"] = "./tests"

            with open(json_case_path, "w") as f:
                json.dump(workflow_dict, f)

            workflow = Workflow(workflow=json_case_path)

            current_dir = os.getcwd()

            # change current working directory back
            os.chdir("../")

            self.assertEqual(
                logobs.output[1],
                "INFO:root:Change current working path to the specified path.",
            )

            os.chdir(current_dir)

        with self.assertLogs() as logobs:
            # Change working_dir value in the json file to a valid path in Win format
            with open(json_case_path, "r") as f:
                workflow_dict = json.load(f)
                workflow_dict["working_dir"] = ".\\tests"

            with open(json_case_path, "w") as f:
                json.dump(workflow_dict, f)

            workflow = Workflow(workflow=json_case_path)

            current_dir = os.getcwd()

            # Change current working directory back
            os.chdir("../")

            self.assertEqual(
                logobs.output[1],
                "INFO:root:Change current working path to the specified path.",
            )

            os.chdir(current_dir)

    def test_valid_absolute_dir(self):
        """This test checks when a absolute working directory is provided and it also points to the correct path,
        if the program will behave correctly"""
        with self.assertLogs() as logobs:
            json_case_path = "./tests/api/data/flexible_calling_unit_test/verification_case_unit_test_Path.json"

            # Change working_dir value in the json file to a valid path
            print(os.getcwd())

            with open(json_case_path, "r") as f:
                workflow_dict = json.load(f)
                if platform.system() == "Windows":
                    workflow_dict["working_dir"] = os.getcwd() + "\\tests\\api\\result"
                else:
                    workflow_dict["working_dir"] = os.getcwd() + "/tests/api/result"

            with open(json_case_path, "w") as f:
                json.dump(workflow_dict, f)

            workflow = Workflow(workflow=json_case_path)

            current_dir = os.getcwd()

            # change current working directory back
            os.chdir("../../..")

            self.assertEqual(
                logobs.output[1],
                "INFO:root:Change current working path to the specified path.",
            )

            os.chdir(current_dir)

    def test_dir_not_exist(self):
        """This test checks when a valid wd is provided but it doesn't exist,
        if the program will behave correctly"""
        with self.assertLogs() as logobs:
            json_case_path = "./tests/api/data/flexible_calling_unit_test/verification_case_unit_test_Path.json"

            # Change working_dir value in the json file to a path that does not exist
            with open(json_case_path, "r") as f:
                workflow_dict = json.load(f)
                workflow_dict["working_dir"] = "./tests/api/result/not_existing_path"

            with open(json_case_path, "w") as f:
                json.dump(workflow_dict, f)

            workflow = Workflow(workflow=json_case_path)

            current_dir = os.getcwd()

            self.assertEqual(
                logobs.output[1],
                "INFO:root:working directory specified does not exist and create a new director.",
            )

            # then delete this path.
            os.rmdir("./tests/api/result/not_existing_path")

    def test_dir_without_seperator(self):
        """This test checks when a working directory without any "/" or "\\" is provided and it also points to the correct path,
        if the program will behave correctly"""
        with self.assertLogs() as logobs:
            json_case_path = "./tests/api/data/flexible_calling_unit_test/verification_case_unit_test_Path.json"

            # Change working_dir value in the json file to a valid path
            with open(json_case_path, "r") as f:
                workflow_dict = json.load(f)
                workflow_dict["working_dir"] = "tests"

            with open(json_case_path, "w") as f:
                json.dump(workflow_dict, f)

            workflow = Workflow(workflow=json_case_path)

            current_dir = os.getcwd()

            # change current working directory back
            os.chdir("../")

            self.assertEqual(
                logobs.output[0],
                "INFO:root:Change current working path to the specified path.",
            )

            os.chdir(current_dir)


if __name__ == "__main__":
    unittest.main()
