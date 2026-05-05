import datetime
import sys
import os
import unittest
import subprocess
import json
from pathlib import Path

sys.path.append("./constrain")


class TestBrickDemoIntegration(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        # Get the absolute path to the project root
        current_dir = Path(__file__).parent
        project_root = current_dir.parent
        self.demo_path = project_root / "constrain" / "demo" / "brick"
        self.data_path = self.demo_path / "data"
        self.script_file = self.demo_path / "brick_workflow_demo.py"

        # Expected output files
        self.report_file = self.data_path / "report_summary.md"
        self.query_result_file = self.data_path / "query_result.json"
        self.case1_json = self.data_path / "1_md.json"
        self.case2_json = self.data_path / "2_md.json"
        self.case1_md = self.data_path / "case-1.md"
        self.case2_md = self.data_path / "case-2.md"

        # Clean up any existing output files
        output_files = [
            self.report_file,
            self.query_result_file,
            self.case1_json,
            self.case2_json,
            self.case1_md,
            self.case2_md,
        ]

        for file_path in output_files:
            if file_path.exists():
                file_path.unlink()

        # Clean up result directories
        result_dirs = [
            self.data_path / "VerificationCase1",
            self.data_path / "VerificationCase2",
        ]

        for dir_path in result_dirs:
            if dir_path.exists():
                import shutil

                shutil.rmtree(dir_path)

    def tearDown(self):
        """Clean up after test"""
        # Optionally clean up generated files
        pass

    def test_brick_demo_workflow_runs_successfully(self):
        """Test that brick_workflow_demo.py script runs successfully and generates expected outputs"""

        # Verify the script file exists
        self.assertTrue(
            self.script_file.exists(), f"Script file {self.script_file} does not exist"
        )

        # Change to the demo directory and run the script
        original_cwd = os.getcwd()
        try:
            os.chdir(self.demo_path)

            # Run the brick_workflow_demo.py script
            result = subprocess.run(
                ["poetry", "run", "python", "brick_workflow_demo.py"],
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            # Check that the script ran successfully
            self.assertEqual(
                result.returncode,
                0,
                f"Script failed with return code {result.returncode}.\n"
                f"STDOUT: {result.stdout}\n"
                f"STDERR: {result.stderr}",
            )

            # Check for success message in output
            self.assertIn(
                "Congratulations! the demo workflow is executed with expected results and no error!",
                result.stdout,
                "Expected success message not found in output",
            )

        finally:
            os.chdir(original_cwd)

    def test_expected_output_files_generated(self):
        """Test that all expected output files are generated"""

        # Run the workflow first
        self.test_brick_demo_workflow_runs_successfully()

        # Verify that all expected files were generated
        expected_files = [
            self.report_file,
            self.query_result_file,
            self.case1_json,
            self.case2_json,
            self.case1_md,
            self.case2_md,
        ]

        for file_path in expected_files:
            self.assertTrue(
                file_path.exists(),
                f"Expected output file {file_path} was not generated",
            )

        # Verify result directories exist
        result_dirs = [
            self.data_path / "VerificationCase1",
            self.data_path / "VerificationCase2",
        ]

        for dir_path in result_dirs:
            self.assertTrue(
                dir_path.exists() and dir_path.is_dir(),
                f"Expected result directory {dir_path} was not created",
            )

    def test_report_summary_validation(self):
        """Test that the report summary has expected content and all verifications pass"""

        # Run the workflow first if report doesn't exist
        if not self.report_file.exists():
            self.test_brick_demo_workflow_runs_successfully()

        # Read and parse the report file
        with open(self.report_file, "r") as f:
            report_content = f.read()

        # Verify the report is not empty
        self.assertGreater(len(report_content.strip()), 0, "Report file is empty")

        # Check for expected header
        self.assertIn(
            "# Verification Results:",
            report_content,
            "Report should contain the expected header",
        )

        # Parse the markdown table to extract verification results
        lines = report_content.strip().split("\n")

        # Find the table header and data rows
        table_started = False
        data_rows = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Skip the header and separator lines
            if line.startswith("| Case No.") or line.startswith("| ----"):
                table_started = True
                continue

            # Process data rows
            if table_started and line.startswith("|") and line.endswith("|"):
                # Split the line by | and clean up whitespace
                columns = [
                    col.strip() for col in line.split("|")[1:-1]
                ]  # Remove empty first/last elements
                if len(columns) >= 7:  # Ensure we have all expected columns
                    data_rows.append(columns)

        # Verify we found exactly 2 data rows (for zone_1 and zone_2)
        self.assertEqual(
            len(data_rows), 2, f"Expected 2 data rows, found {len(data_rows)}"
        )

        # Check each verification case
        for i, row in enumerate(data_rows):
            case_no = row[0].strip()
            data_source = row[1].strip()
            verification_class = row[2].strip()
            sample_count = row[3].strip()
            pass_count = row[4].strip()
            fail_count = row[5].strip()
            untested_count = row[6].strip()
            verification_passed = row[7].strip() if len(row) > 7 else ""

            # Verify expected values
            self.assertEqual(
                data_source,
                "EnergyPlus_data",
                f"Case {case_no}: Expected data source 'EnergyPlus_data', got '{data_source}'",
            )

            self.assertEqual(
                verification_class,
                "ZoneTempControl",
                f"Case {case_no}: Expected verification class 'ZoneTempControl', got '{verification_class}'",
            )

            # Verify that sample count equals pass count (all samples passed)
            self.assertEqual(
                sample_count,
                pass_count,
                f"Case {case_no}: Sample count ({sample_count}) "
                f"does not equal pass count ({pass_count}). "
                f"Fail count: {fail_count}, Untested count: {untested_count}",
            )

            # Verify that fail count is 0
            self.assertEqual(
                fail_count,
                "0",
                f"Case {case_no}: Expected 0 failures, got {fail_count}",
            )

            # Verify that untested count is 0
            self.assertEqual(
                untested_count,
                "0",
                f"Case {case_no}: Expected 0 untested, got {untested_count}",
            )

            # Verify that verification passed is True
            self.assertEqual(
                verification_passed,
                "True",
                f"Case {case_no}: Verification should have passed",
            )

            # Verify sample count is expected value (8760 for hourly data)
            self.assertEqual(
                sample_count,
                "8760",
                f"Case {case_no}: Expected 8760 samples (hourly data), got {sample_count}",
            )

    def test_json_output_validation(self):
        """Test that the JSON output files contain expected structure and data"""

        # Run the workflow first if files don't exist
        if not self.case1_json.exists():
            self.test_brick_demo_workflow_runs_successfully()

        # Test query_result.json
        with open(self.query_result_file, "r") as f:
            query_result = json.load(f)

        # Verify query result structure
        self.assertIsInstance(query_result, dict, "Query result should be a dictionary")
        self.assertGreater(len(query_result), 0, "Query result should not be empty")

        # Test case JSON files
        json_files = [self.case1_json, self.case2_json]

        for i, json_file in enumerate(json_files, 1):
            with open(json_file, "r") as f:
                case_data = json.load(f)

            # Verify JSON structure
            self.assertIn(str(i), case_data, f"Case {i} data should contain key '{i}'")
            case_info = case_data[str(i)]

            # Verify required keys
            required_keys = [
                "md_content",
                "outcome_notes",
                "model_file",
                "verification_class",
            ]
            for key in required_keys:
                self.assertIn(key, case_info, f"Case {i} should contain key '{key}'")

            # Verify outcome_notes structure
            outcome_notes = case_info["outcome_notes"]
            expected_outcome_keys = [
                "Sample #",
                "Pass #",
                "Fail #",
                "Untested #",
                "Verification Passed?",
            ]
            for key in expected_outcome_keys:
                self.assertIn(
                    key,
                    outcome_notes,
                    f"Case {i} outcome_notes should contain key '{key}'",
                )

            # Verify verification passed
            self.assertTrue(
                outcome_notes["Verification Passed?"],
                f"Case {i} should have passed verification",
            )

            # Verify all samples passed
            self.assertEqual(
                outcome_notes["Sample #"],
                outcome_notes["Pass #"],
                f"Case {i}: All samples should pass",
            )

            self.assertEqual(
                outcome_notes["Fail #"], 0, f"Case {i}: Should have 0 failures"
            )

            # Verify verification class
            self.assertEqual(
                case_info["verification_class"],
                "ZoneTempControl",
                f"Case {i}: Expected verification class 'ZoneTempControl'",
            )

    def test_markdown_case_files_validation(self):
        """Test that the markdown case files contain expected content"""

        # Run the workflow first if files don't exist
        if not self.case1_md.exists():
            self.test_brick_demo_workflow_runs_successfully()

        # Test case markdown files
        md_files = [self.case1_md, self.case2_md]

        for i, md_file in enumerate(md_files, 1):
            with open(md_file, "r") as f:
                md_content = f.read()

            # Verify content is not empty
            self.assertGreater(
                len(md_content.strip()),
                0,
                f"Case {i} markdown file should not be empty",
            )

            # Verify expected sections
            expected_sections = [
                f"## Results for Verification Case ID {i}",
                "### Pass/Fail check result",
                "### Result visualization",
                "### Verification case definition",
            ]

            for section in expected_sections:
                self.assertIn(
                    section,
                    md_content,
                    f"Case {i} markdown should contain section '{section}'",
                )

            # Verify verification passed in content
            self.assertIn(
                "'Verification Passed?': True",
                md_content,
                f"Case {i} should show verification passed",
            )

    def test_workflow_end_to_end(self):
        """Comprehensive end-to-end test of the entire brick demo workflow"""

        # This test combines all the individual tests to ensure the complete workflow works
        self.test_brick_demo_workflow_runs_successfully()
        self.test_expected_output_files_generated()
        self.test_report_summary_validation()
        self.test_json_output_validation()
        self.test_markdown_case_files_validation()


if __name__ == "__main__":
    unittest.main()
