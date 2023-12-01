import os
import sys
import unittest

sys.path.append("./constrain")
from api import Reporting

verification_json = "./tests/api/data/verification_output/*_md.json"
result_md_name = "testing.md"
result_md_path = "./tests/api/data/verification_output/testing.md"
report_format = "markdown"


class TestReporting(unittest.TestCase):
    def test_constructor_wrong_arg_type(self):
        # wrong `verification_json` type
        with self.assertLogs() as logobs:
            Reporting({verification_json}, result_md_name, report_format)
            self.assertEqual(
                "ERROR:root:The type of the `verification_json` arg needs to be a str. It cannot be <class 'set'>.",
                logobs.output[0],
            )

        # wrong `result_md_path` type
        with self.assertLogs() as logobs:
            Reporting(verification_json, [result_md_name], report_format)
            self.assertEqual(
                "ERROR:root:The type of the `result_md_name` arg needs to be a str. It cannot be <class 'list'>.",
                logobs.output[0],
            )

        # wrong `report_format` type
        with self.assertLogs() as logobs:
            Reporting(verification_json, result_md_name, [report_format])
            self.assertEqual(
                "ERROR:root:The type of the `report_format` arg needs to be a str. It cannot be <class 'list'>.",
                logobs.output[0],
            )

    def test_report_multiple_cases(self):
        reporting_obj = Reporting(verification_json, result_md_name, report_format)

        # report only selective verification results
        reporting_obj.report_multiple_cases(item_names=["AutomaticOADamperControl"])
        self.assertTrue(os.path.isfile(result_md_path))
        os.remove(result_md_path)

        # report all the verification results
        reporting_obj.report_multiple_cases(item_names=[])
        self.assertTrue(os.path.isfile(result_md_path))
        os.remove(result_md_path)

    def test_report_multiple_cases_wrong_arg_type(self):
        reporting_obj = Reporting(verification_json, result_md_name, report_format)

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
        reporting_obj = Reporting(verification_json, result_md_name, report_format)

        # wrong verification item name
        with self.assertLogs() as logobs:
            reporting_obj.report_multiple_cases(["not_existing_verification_item"])
            self.assertEqual(
                "ERROR:root:not_existing_verification_item is not part of the read files.",
                logobs.output[0],
            )


if __name__ == "__main__":
    unittest.main()
