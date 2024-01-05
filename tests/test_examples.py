import unittest, os, re
import pandas as pd

from constrain.examples import Examples
from constrain.api import VerificationCase
from constrain.api import Verification
from constrain.api import Reporting


class TestExamples(unittest.TestCase):
    def test_examples_1(self):
        ex = Examples()
        # Check that files exists
        assert os.path.isfile(ex.library())
        assert os.path.isfile(ex.verifications("example_1"))

        # Check that data can be loaded
        data = ex.data("example_1")
        assert isinstance(data, pd.DataFrame)
        assert len(data) > 1

        # Run example
        cases = VerificationCase(json_case_path=ex.verifications("example_1"))
        cases.validate()
        verif = Verification(verifications=cases)
        verif.configure(
            output_path="./",
            lib_items_path=ex.library(),
            plot_option="all-expand",
            fig_size=(10, 5),
            num_threads=1,
            preprocessed_data=data,
        )
        verif.run()
        reporting = Reporting(
            verification_json="./*_md.json",
            result_md_name="report_summary.md",
            report_format="markdown",
        )
        reporting.report_multiple_cases()
        assert os.path.isfile("./report_summary.md")
        summary = open("./report_summary.md", "r").read()
        res = re.findall("False", summary)
        assert len(res) == 3
