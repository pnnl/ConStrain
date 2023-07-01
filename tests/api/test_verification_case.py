import json
import os, sys, unittest, copy


sys.path.append("./src")

from api import VerificationCase


class TestVerificaqtionCase(unittest.TestCase):
    case = {
        "no": 1,
        "run_simulation": True,
        "simulation_IO": {
            "idf": "../test_cases/doe_prototype_cases/ASHRAE901_Hospital_STD2019_Atlanta_Case1.idf",
            "idd": "../resources/Energy+V9_0_1.idd",
            "weather": "../weather/USA_GA_Atlanta-Hartsfield.Jackson.Intl.AP.722190_TMY3.epw",
            "output": "eplusout.csv",
            "ep_path": "C:\\EnergyPlusV9-0-1\\energyplus.exe",
        },
        "expected_result": "pass",
        "datapoints_source": {
            "idf_output_variables": {
                "T_sa_set": {
                    "subject": "VAV_1 Supply Equipment Outlet Node",
                    "variable": "System Node Setpoint Temperature",
                    "frequency": "detailed",
                }
            },
            "parameters": {"T_z_coo": 24.0},
        },
        "verification_class": "SupplyAirTempReset",
    }

    json_case_path = (
        "./tests/api/data/verification_case_unit_test/verification_case_unit_test.json"
    )

    example_base_case = {
        "no": 1,
        "run_simulation": True,
        "simulation_IO": {
            "idf": "../testing.idf",
            "idd": "../Energy+V9_0_1.idd",
            "weather": "./USA_GA_Atlanta-Hartsfield.Jackson.Intl.AP.722190_TMY3.epw",
            "output": "eplusout.csv",
            "ep_path": "C:\\EnergyPlusV9-0-1\\energyplus.exe",
        },
        "expected_result": "fail",
        "datapoints_source": {
            "idf_output_variables": {
                "oa_flow": {
                    "subject": "VAV_1_OAInlet Node",
                    "variable": "System Node Standard Density Volume Flow Rate",
                    "frequency": "TimeStep",
                },
                "oa_db": {
                    "subject": "Environment",
                    "variable": "Site Outdoor Air Drybulb Temperature",
                    "frequency": "TimeStep",
                },
            },
            "parameters": {"oa_threshold": 300},
        },
        "verification_class": "Testing",
    }
    update_key_value = {
        "simulation_IO": {
            "idf": ["Testing_file1.idf", "Testing_file2.idf"],
        },
        "datapoints_source": {
            "idf_output_variables": {
                "oa_flow": {
                    "subject": ["VAV_1_OAInlet Node", "VAV_2_OAInlet Node"],
                    "variable": [
                        "System Node Standard Density Volume Flow Rate",
                        "Current Density Volume",
                    ],
                },
                "oa_db": {
                    "variable": [
                        "Site Outdoor Air Drybulb Temperature",
                        "Site Outdoor Air Relative Humidity",
                    ],
                },
            },
            "parameters": {"oa_threshold": [999, 1000]},
        },
    }

    def test_constructor_none(self):
        assert VerificationCase(cases=None, json_case_path=None).case_suite == {}

    def test_constructor_valid_cases(self):
        cases = [self.case]
        vc = VerificationCase(cases=cases, json_case_path=None)
        popped_case = vc.case_suite.popitem()
        cases[0]["case_id_in_suite"] = popped_case[0]
        assert popped_case[1] == cases[0]

    def test_constructor_invalid_cases(self):
        with self.assertLogs() as logobs:
            testing_case = {"cases": self.case}  # wrong data type
            vc = VerificationCase(cases=testing_case, json_case_path=None)
            self.assertEqual(
                "ERROR:root:The `cases` argument's type must be typing.List, but <class 'dict'> is provided.",
                logobs.output[0],
            )

    def test_constructor_valid_path(self):
        vc = VerificationCase(cases=None, json_case_path=self.json_case_path)
        assert len(vc.case_suite) == 2

    def test_constructor_valid_cases_and_path(self):
        cases = [copy.deepcopy(self.case)]
        cases[0]["test_duplicate_key"] = "test_duplicate_value"
        vc = VerificationCase(cases=cases, json_case_path=self.json_case_path)
        assert len(vc.case_suite) == 3

    def test_constructor_invalid_path(self):
        # test when the `json_case_path` doesn't exist
        with self.assertLogs() as logobs:
            json_case_path = "./not_existing_path/testing.json"
            VerificationCase(cases=None, json_case_path=json_case_path)
            self.assertEqual(
                f"ERROR:root:`./not_existing_path/testing.json' doesn't exist. Please make sure that the 'json_case_path' argument is correct.",
                logobs.output[0],
            )

        # test when the wrong `json_case_path` type is provided
        with self.assertLogs() as logobs:
            json_case_path = ["wrong_file_path_type.json"]
            VerificationCase(cases=None, json_case_path=json_case_path)
            self.assertEqual(
                "ERROR:root:The `json_case_path` argument's type must be <class 'str'>, but <class "
                "'list'> is provided.",
                logobs.output[0],
            )

        # test when the given `json_case_path` directory doesn't exist
        with self.assertLogs() as logobs:
            json_case_path = "./not_existing_path"
            VerificationCase(cases=None, json_case_path=json_case_path)
            self.assertEqual(
                "ERROR:root:The provided directory doesn't exist. Please make sure to provide a correct `json_case_path`.",
                logobs.output[0],
            )

    def test_constructor_dir_path(self):
        # test whether the json files in the given directory `json_case_path` are read correctly
        json_case_path = "./tests/api/data/verification_case_unit_test/"
        vc = VerificationCase(cases=None, json_case_path=json_case_path)
        assert len(vc.case_suite) == 4

    def test_load_verification_cases_from_json_invalid_path(self):
        with self.assertLogs() as logobs:
            vc = VerificationCase(cases=None, json_case_path=None)
            vc.load_verification_cases_from_json(["wrong_file_path_type.json"])
            self.assertEqual(
                "ERROR:root:The `json_case_path` argument's type must be <class 'str'>, but <class 'list'> is provided.",
                logobs.output[0],
            )

    def test_load_verification_cases_from_json_with_duplicate_cases(self):
        json_case_path = "./tests/api/data/verification_case_unit_test/verification_case_unit_test.json"
        vc = VerificationCase(cases=[self.case], json_case_path=None)
        list_of_hash = vc.load_verification_cases_from_json(json_case_path)
        assert len(list_of_hash) == 1
        assert len(vc.case_suite) == 2

    def test_save_case_suite_to_json_invalid_path(self):
        # test when `json_path` doesn't exist
        with self.assertLogs() as logobs:
            vc = VerificationCase(
                cases=None,
                json_case_path="./tests/api/data/verification_case_unit_test/verification_case_unit_test.json",
            )
            vc.save_case_suite_to_json(["./not_existing_dir/testing.json"])
            self.assertEqual(
                "ERROR:root:The `json_path` argument's type must be <class 'str'>, but <class "
                "'list'> is provided.",
                logobs.output[0],
            )

    def test_save_case_suite_to_json_invalid_caseid(self):
        # test when wrong `case_ids` type is provided
        with self.assertLogs() as logobs:
            vc = VerificationCase(
                cases=None,
                json_case_path="./tests/api/data/verification_case_unit_test/verification_case_unit_test.json",
            )
            vc.save_case_suite_to_json(
                json_path="./testing.json", case_ids="this is wrong case_ids type"
            )
            self.assertEqual(
                "ERROR:root:The `case_ids` argument's type must be typing.List, but <class "
                "'str'> is provided.",
                logobs.output[0],
            )

    def test_save_case_suite_to_json_valid(self):
        # test the given case is saved correctly.
        saving_file_path = "./tests/api/result/from_test_save_case_suite_to_json_check_file_saving.json"
        vc = VerificationCase(
            cases=None,
            json_case_path="./tests/api/data/verification_case_unit_test/verification_case_unit_test.json",
        )
        vc.save_case_suite_to_json(saving_file_path)
        assert os.path.isfile(saving_file_path)
        os.remove(saving_file_path)

    def test_save_case_suite_to_json_all_cases(self):
        saving_file_path = "./tests/api/result/from_test_save_case_suite_to_json_check_file_saving.json"
        cases = [{"fake_case_key": f"fake_case_value_{i}"} for i in range(3)]
        vc = VerificationCase(
            cases=cases,
            json_case_path="./tests/api/data/verification_case_unit_test/verification_case_unit_test.json",
        )
        vc.save_case_suite_to_json(saving_file_path)

        with open(saving_file_path, "r") as f:
            loaded_cases = json.load(f)
        num_cases = len(loaded_cases["cases"])
        assert num_cases == 5  # 3 ram cases and 2 file cases
        os.remove(saving_file_path)

    def test_save_case_suite_to_json_by_partial_valid_caseid(self):
        saving_file_path = "./tests/api/result/from_test_save_case_suite_to_json_check_file_saving.json"
        cases = [{"fake_case_key": f"fake_case_value_{i}"} for i in range(3)]

        with self.assertLogs() as logobs:
            vc = VerificationCase(
                cases=cases,
                json_case_path="./tests/api/data/verification_case_unit_test/verification_case_unit_test.json",
            )
            suite_keys = list(vc.case_suite.keys())
            partial_good_keys = suite_keys[:2] + ["wrong-key-1", 2]
            vc.save_case_suite_to_json(saving_file_path, case_ids=partial_good_keys)
            self.assertEqual(
                "WARNING:root:case_id wrong-key-1 is not in self.case_suite!",
                logobs.output[0],
            )
            self.assertEqual(
                "WARNING:root:case_id 2 is not in self.case_suite!",
                logobs.output[1],
            )

        with open(saving_file_path, "r") as f:
            loaded_cases = json.load(f)
        num_cases = len(loaded_cases["cases"])
        assert num_cases == 2
        os.remove(saving_file_path)

    def test_create_verification_case_suite_from_base_case_valid(self):
        returned_updated_base_cases_list = (
            VerificationCase.create_verification_case_suite_from_base_case(
                self.example_base_case, self.update_key_value, keep_base_case=True
            )
        )
        assert len(returned_updated_base_cases_list) == 3

    def test_create_verification_case_suite_from_base_case_invalid_basecase(self):
        with self.assertLogs() as logobs:
            wrong_base_case_type = [{"wrong_base_case_type_key": "testing"}]
            VerificationCase.create_verification_case_suite_from_base_case(
                wrong_base_case_type, self.update_key_value, keep_base_case=False
            )
            self.assertEqual(
                "ERROR:root:The `base_case` argument type must be Dict, but <class 'list'> type is provided.",
                logobs.output[0],
            )

    def test_create_verification_case_suite_from_base_case_invalid_update_dict(self):
        with self.assertLogs() as logobs:
            wrong_update_key_value_type = [{"wrong_update_key_type_key": "testing"}]
            VerificationCase.create_verification_case_suite_from_base_case(
                self.example_base_case,
                wrong_update_key_value_type,
                keep_base_case=False,
            )
            self.assertEqual(
                "ERROR:root:The `update_key_value` argument type must be Dict, but <class 'list'> type is provided.",
                logobs.output[0],
            )

    def test_create_verification_case_suite_from_base_case_invalid_keep_flag(self):
        with self.assertLogs() as logobs:
            VerificationCase.create_verification_case_suite_from_base_case(
                self.example_base_case, self.update_key_value, keep_base_case="Fail"
            )
            self.assertEqual(
                "ERROR:root:The `keep_base_case` argument must be bool, but <class 'str'> type is provided.",
                logobs.output[0],
            )

    def test_create_verification_case_suite_from_base_case_wrong_length(self):
        with self.assertLogs() as logobs:
            wrong_update_key_value = copy.deepcopy(self.update_key_value)
            wrong_update_key_value["datapoints_source"]["parameters"][
                "oa_threshold"
            ] = [
                999,
                1000,
                1200,
            ]  # intentionally add wrong length of list (should be length of 2 list)

            VerificationCase.create_verification_case_suite_from_base_case(
                self.example_base_case, wrong_update_key_value, keep_base_case=False
            )
            self.assertEqual(
                "ERROR:root:The length of modifying values in lists must be the same.",
                logobs.output[0],
            )

    def test_validate_verification_case_structure_valid(self):
        assert VerificationCase.validate_verification_case_structure(self.case)

    def test_validate_verification_case_structure_invalid_case_type(self):
        # test when wrong case type is provided.
        with self.assertLogs() as logobs:
            case = []
            validation_result = VerificationCase.validate_verification_case_structure(
                case
            )
            self.assertFalse(validation_result)
            self.assertEqual(
                "ERROR:root:The case argument type must be dict, but <class 'list'> is provided.",
                logobs.output[0],
            )

    def test_validate_verification_case_structure_wrong_verbose_flag(self):
        with self.assertLogs() as logobs:
            case = {}
            verbose = "pass"
            validation_result = VerificationCase.validate_verification_case_structure(
                case, verbose
            )
            self.assertFalse(validation_result)
            self.assertEqual(
                "ERROR:root:The verbose argument type must be bool, but <class 'str'> is provided.",
                logobs.output[0],
            )

    def test_validate_verification_case_structure_wrong_leaf_value(self):
        with self.assertLogs() as logobs:
            case_wrong_run_simulation = copy.deepcopy(self.case)
            case_wrong_run_simulation["run_simulation"] = "PASS"  # supposed to be True
            validation_result = VerificationCase.validate_verification_case_structure(
                case_wrong_run_simulation
            )
            self.assertFalse(validation_result)
            self.assertEqual(
                "ERROR:root:The type of 'run_simulation' key must be <class 'bool'>, but <class 'str'> is provided.",
                logobs.output[0],
            )

    def test_validate_verification_case_structure_missing_leaf_key(self):
        with self.assertLogs() as logobs:
            case_missing_subject = copy.deepcopy(self.case)
            del case_missing_subject["simulation_IO"][
                "output"
            ]  # intentionally missed subject key
            validation_result = VerificationCase.validate_verification_case_structure(
                case_missing_subject
            )
            self.assertFalse(validation_result)
            self.assertTrue(
                "ERROR:root:Missing required key 'output' in" in logobs.output[0]
            )

    def test_validate_verification_case_structure_datapoints_test_valid(self):
        case = copy.deepcopy(self.case)
        case["datapoints_source"]["idf_output_variables"]["T_ra_set"] = {
            "subject": "VAV_1 Return Equipment Outlet Node",
            "variable": "System Node Setpoint Temperature",
            "frequency": "detailed",
        }
        case["datapoints_source"]["parameters"]["parameter2"] = 33
        validation_result = VerificationCase.validate_verification_case_structure(case)
        assert validation_result

    def test_validate_verification_case_structure_datapoints_test_invalid(self):
        with self.assertLogs() as logobs:
            case = copy.deepcopy(self.case)
            case["datapoints_source"]["parameters"]["parameter2"] = "33"
            validation_result = VerificationCase.validate_verification_case_structure(
                case
            )
            assert not validation_result
            self.assertEqual(
                "ERROR:root:The type of 'parameter2' key must be <class 'float'>, but <class 'str'> is provided.",
                logobs.output[0],
            )

    def test_save_verification_cases_to_json(self):
        json_path = "./tests/api/result/wrong_json_path.json"

        # when wrong `json_path` type is provided
        with self.assertLogs() as logobs:
            wrong_json_path = ["./wrong_json_path.json"]
            VerificationCase.save_verification_cases_to_json(
                wrong_json_path, [self.case]
            )
            self.assertEqual(
                "ERROR:root:The `json_path` argument type must be str, but <class 'list'> is provided.",
                logobs.output[0],
            )

        # when wrong `cases` type is provided
        with self.assertLogs() as logobs:
            VerificationCase.save_verification_cases_to_json(json_path, self.case)
            self.assertEqual(
                "ERROR:root:The `cases` argument type must be list, but <class 'dict'> is provided.",
                logobs.output[0],
            )

        # when wrong `json_path` extension is provided
        with self.assertLogs() as logobs:
            wrong_json_path = "./wrong_json_path.csv"
            VerificationCase.save_verification_cases_to_json(
                wrong_json_path, [self.case]
            )
            self.assertEqual(
                "ERROR:root:The `json_path` argument must end with '.json' extension.",
                logobs.output[0],
            )

        # test when correct `json_path` and `cases` arguments are provided
        VerificationCase.save_verification_cases_to_json(json_path, [self.case])
        assert os.path.isfile(json_path)
        os.remove(json_path)


if __name__ == "__main__":
    unittest.main()
