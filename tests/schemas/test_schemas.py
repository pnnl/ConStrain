import unittest
import numpy as np
import pandas as pd
import jsonschema
import json
import copy


class JSONSchemaTest(unittest.TestCase):
    def setUp(self):
        workflow_schema_path = "./constrain/schema/workflow.schema.json"
        library_item_schema_path = "./constrain/schema/library.schema.json"
        verification_cases_schema_path = (
            "./constrain/schema/verification_cases.schema.json"
        )

        with open(workflow_schema_path, "r") as f:
            self.workflow_schema = json.load(f)

        with open(library_item_schema_path, "r") as f:
            self.library_item_schema = json.load(f)

        with open(verification_cases_schema_path, "r") as f:
            self.verification_cases_schema = json.load(f)

    def test_workflow_schema_pass(self):
        workflow_path = "./constrain/demo/G36_demo/G36_demo_workflow.json"

        with open(workflow_path, "r") as f:
            workflow_dict = json.load(f)

        try:
            jsonschema.validate(instance=workflow_dict, schema=self.workflow_schema)
        except Exception as e:
            self.fail(f"Validation failed: {e}")

    def test_workflow_schema_fail(self):
        workflow_path = "./constrain/demo/G36_demo/G36_demo_workflow.json"

        with open(workflow_path, "r") as f:
            workflow_dict = json.load(f)

        del workflow_dict["states"]

        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(instance=workflow_dict, schema=self.workflow_schema)

    def test_workflow_schema_allows_working_dir(self):
        workflow_path = "./constrain/demo/G36_demo/G36_demo_workflow.json"

        with open(workflow_path, "r") as f:
            workflow_dict = json.load(f)

        workflow_dict["working_dir"] = "./demo/api_demo"

        try:
            jsonschema.validate(instance=workflow_dict, schema=self.workflow_schema)
        except Exception as e:
            self.fail(f"Validation failed: {e}")

    def test_workflow_schema_allows_all_logical_choice(self):
        workflow_path = "./constrain/demo/G36_demo/G36_demo_workflow.json"

        with open(workflow_path, "r") as f:
            workflow_dict = json.load(f)

        workflow_dict = copy.deepcopy(workflow_dict)
        workflow_dict["states"]["check original case length"]["Choices"] = [
            {
                "ALL": [
                    {
                        "Value": "len(Payloads['original_case_keys']) == 3",
                        "Equals": "True",
                        "Next": "validate cases",
                    },
                    {
                        "Value": "'verification_case_obj' in Payloads",
                        "Equals": "True",
                        "Next": "validate cases",
                    },
                ],
                "Next": "validate cases",
            }
        ]

        try:
            jsonschema.validate(instance=workflow_dict, schema=self.workflow_schema)
        except Exception as e:
            self.fail(f"Validation failed: {e}")

    def test_verification_cases_schema(self):
        verification_case_path = "./tests/schemas/demo_verification_cases.json"

        with open(verification_case_path, "r") as f:
            verification_cases_dict = json.load(f)

        try:
            jsonschema.validate(
                instance=verification_cases_dict, schema=self.verification_cases_schema
            )
        except Exception as e:
            self.fail(f"Validation failed: {e}")

    def test_library_item_schema(self):
        library_item_schema_path = "./constrain/schema/library.json"

        with open(library_item_schema_path, "r") as f:
            library_dict = json.load(f)

        supply_air_temp_reset_lib_item = library_dict["SupplyAirTempReset"]

        try:
            jsonschema.validate(
                instance=supply_air_temp_reset_lib_item, schema=self.library_item_schema
            )
        except Exception as e:
            self.fail(f"Validation failed: {e}")
