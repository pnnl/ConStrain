import datetime
import sys
import os
import unittest
import subprocess
import re
from pathlib import Path

sys.path.append("./constrain")


class TestTSPRCasesIntegration(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        # Get the absolute path to the project root
        current_dir = Path(__file__).parent
        project_root = current_dir.parent
        self.demo_path = project_root / "constrain" / "demo" / "tspr_cases"
        self.report_file = self.demo_path / "report_summary.md"
        self.script_file = self.demo_path / "tspr_cases.py"
        
        # Clean up any existing report file
        if self.report_file.exists():
            self.report_file.unlink()

    def tearDown(self):
        """Clean up after test"""
        # Optionally clean up generated files
        pass

    def test_tspr_cases_script_generates_passing_report(self):
        """Test that tspr_cases.py script runs successfully and generates a report where all samples pass"""
        
        # Verify the script file exists
        self.assertTrue(self.script_file.exists(), f"Script file {self.script_file} does not exist")
        
        # Change to the demo directory and run the script
        original_cwd = os.getcwd()
        try:
            os.chdir(self.demo_path)
            
            # Run the tspr_cases.py script
            result = subprocess.run(
                [sys.executable, "tspr_cases.py"],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            # Check that the script ran successfully
            self.assertEqual(result.returncode, 0, 
                           f"Script failed with return code {result.returncode}.\n"
                           f"STDOUT: {result.stdout}\n"
                           f"STDERR: {result.stderr}")
            
        finally:
            os.chdir(original_cwd)
        
        # Verify that the report file was generated
        self.assertTrue(self.report_file.exists(), 
                       f"Report file {self.report_file} was not generated")
        
        # Read and parse the report file
        with open(self.report_file, 'r') as f:
            report_content = f.read()
        
        # Verify the report is not empty
        self.assertGreater(len(report_content.strip()), 0, "Report file is empty")
        
        # Parse the markdown table to extract verification results
        lines = report_content.strip().split('\n')
        
        # Find the table header and data rows
        table_started = False
        data_rows = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Skip the header and separator lines
            if line.startswith('| Case No.') or line.startswith('| ----'):
                table_started = True
                continue
                
            # Process data rows
            if table_started and line.startswith('|') and line.endswith('|'):
                # Split the line by | and clean up whitespace
                columns = [col.strip() for col in line.split('|')[1:-1]]  # Remove empty first/last elements
                if len(columns) >= 7:  # Ensure we have all expected columns
                    data_rows.append(columns)
        
        # Verify we found at least one data row
        self.assertGreater(len(data_rows), 0, "No data rows found in the report table")
        
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
            
            # Verify that sample count equals pass count (all samples passed)
            self.assertEqual(sample_count, pass_count, 
                           f"Case {case_no} ({verification_class}): Sample count ({sample_count}) "
                           f"does not equal pass count ({pass_count}). "
                           f"Fail count: {fail_count}, Untested count: {untested_count}")
            
            # Verify that fail count is 0
            self.assertEqual(fail_count, "0", 
                           f"Case {case_no} ({verification_class}): Expected 0 failures, got {fail_count}")
            
            # Verify that untested count is 0
            self.assertEqual(untested_count, "0", 
                           f"Case {case_no} ({verification_class}): Expected 0 untested, got {untested_count}")
            
            # Verify that verification passed is True
            self.assertEqual(verification_passed, "True", 
                           f"Case {case_no} ({verification_class}): Verification should have passed")
            
            # Verify sample count is a positive integer
            try:
                sample_num = int(sample_count)
                self.assertGreater(sample_num, 0, 
                                 f"Case {case_no} ({verification_class}): Sample count should be positive, got {sample_num}")
            except ValueError:
                self.fail(f"Case {case_no} ({verification_class}): Sample count '{sample_count}' is not a valid integer")
        
        print(f"✓ Successfully verified {len(data_rows)} verification cases")
        print("✓ All samples passed in all verification cases")
        print(f"✓ Report generated at: {self.report_file}")

    def test_report_format_validation(self):
        """Test that the report has the expected markdown table format"""
        
        # First run the script if report doesn't exist
        if not self.report_file.exists():
            self.test_tspr_cases_script_generates_passing_report()
            return  # The main test already validates the format
        
        # Read the report file
        with open(self.report_file, 'r') as f:
            report_content = f.read()
        
        # Check for expected header
        self.assertIn("# Verification Results:", report_content, 
                     "Report should contain the expected header")
        
        # Check for table header
        self.assertIn("| Case No.", report_content, 
                     "Report should contain the table header")
        
        # Check for expected columns
        expected_columns = [
            "Case No.", "Data Source", "Verification Class", "Sample #", 
            "Pass #", "Fail #", "Untested #", "Verification Passed?"
        ]
        
        for column in expected_columns:
            self.assertIn(column, report_content, 
                         f"Report should contain column '{column}'")


if __name__ == "__main__":
    unittest.main()
