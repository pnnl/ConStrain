import os
import sys
import unittest

sys.path.append("./constrain")
from api import Reporting

VERIFICATION_JSON = "./tests/api/data/verification_output/*_md.json"
RESULT_MD_NAME = "testing.md"
RESULT_MD_PATH = "./tests/api/data/verification_output/testing.md"
REPORT_FORMAT = "markdown"


class TestReporting(unittest.TestCase):
    def test_constructor_wrong_arg_type(self):
        # wrong `verification_json` type
        with self.assertLogs() as logobs:
            Reporting({VERIFICATION_JSON}, RESULT_MD_NAME, REPORT_FORMAT)
            self.assertEqual(
                "ERROR:root:The type of the `verification_json` arg needs to be a str. It cannot be <class 'set'>.",
                logobs.output[0],
            )

        # wrong `result_md_path` type
        with self.assertLogs() as logobs:
            Reporting(VERIFICATION_JSON, [RESULT_MD_NAME], REPORT_FORMAT)
            self.assertEqual(
                "ERROR:root:The type of the `result_md_name` arg needs to be a str. It cannot be <class 'list'>.",
                logobs.output[0],
            )

        # wrong `report_format` type
        with self.assertLogs() as logobs:
            Reporting(VERIFICATION_JSON, RESULT_MD_NAME, [REPORT_FORMAT])
            self.assertEqual(
                "ERROR:root:The type of the `report_format` arg needs to be a str. It cannot be <class 'list'>.",
                logobs.output[0],
            )

    def test_report_multiple_cases(self):
        reporting_obj = Reporting(VERIFICATION_JSON, RESULT_MD_NAME, REPORT_FORMAT)

        # report only selective verification results
        reporting_obj.report_multiple_cases(item_names=["AutomaticOADamperControl"])
        self.assertTrue(os.path.isfile(RESULT_MD_PATH))
        os.remove(RESULT_MD_PATH)

        # report all the verification results
        reporting_obj.report_multiple_cases(item_names=[])
        self.assertTrue(os.path.isfile(RESULT_MD_PATH))
        os.remove(RESULT_MD_PATH)

    def test_report_multiple_cases_wrong_arg_type(self):
        reporting_obj = Reporting(VERIFICATION_JSON, RESULT_MD_NAME, REPORT_FORMAT)

        # wrong `item_names` type
        with self.assertLogs() as logobs:
            reporting_obj.report_multiple_cases(
                {"SupplyAirTempReset", "AutomaticShutdown"}
            )
            self.assertEqual(
                "ERROR:root:The type of the `item_names` arg needs to be List. It cannot be <class 'set'>.",
                logobs.output[0],
            )

    def test_report_multiple_cases_wrong_verification_name(self):
        reporting_obj = Reporting(VERIFICATION_JSON, RESULT_MD_NAME, REPORT_FORMAT)

        # wrong verification item name
        with self.assertLogs() as logobs:
            reporting_obj.report_multiple_cases(["not_existing_verification_item"])
            self.assertEqual(
                "ERROR:root:not_existing_verification_item is not part of the read files.",
                logobs.output[0],
            )


if __name__ == "__main__":
    unittest.main()
