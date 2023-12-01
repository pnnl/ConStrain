"""
reporting.py
====================================
Reporting API
"""

import glob
import json
import logging
import sys
import os
from typing import List

sys.path.append("..")


class Reporting:
    def __init__(
        self,
        verification_json: str = None,
        result_md_name: str = None,
        report_format: str = "markdown",
    ) -> None:
        """
        Args:
            verification_json (str): Path to the result json files after verifications to be loaded for reporting. It can be one JSON file or wildcard for multiple JSON files (e.g., *_md.json).
            result_md_name (str): Name of the report summary markdown to be saved. All md reports will be created in the same directory as the verification result json files.
            report_format (str): File format to be output. For now, only `markdown` format  is available. More formats (e.g., html, pdf, csv, etc.) will be added in future releases.
        """

        # TODO:
        #  - this class is largely duplicate of summarize_md.py. Need to merge the two (while not losing the other file as we are still using it for large scale runs.

        self.verification_json = verification_json
        self.result_md_name = result_md_name
        self.report_format = report_format

        if not (isinstance(self.verification_json, str)):
            logging.error(
                f"The type of the `verification_json` arg needs to be a str. It cannot be {type(self.verification_json)}."
            )
            return None

        if not isinstance(self.result_md_name, str):
            logging.error(
                f"The type of the `result_md_name` arg needs to be a str. It cannot be {type(self.result_md_name)}."
            )
            return None

        if not isinstance(self.report_format, str):
            logging.error(
                f"The type of the `report_format` arg needs to be a str. It cannot be {type(self.report_format)}."
            )
            return None

        if self.report_format != "markdown":  # TODO: to be deleted later
            logging.error(
                f"Only `markdown` format is available. More formats will be added in the future release."
            )
            return None

        self.result_md_dir = os.path.dirname(self.verification_json)
        self.result_md_path = f"{self.result_md_dir}/{self.result_md_name}"
        self.md_dict_dump = {}
        self.verification_item_case_id_mapping = {}

        # TODO: refactor below to make mapping creation more efficient
        for json_file in glob.glob(self.verification_json):
            with open(json_file) as fr:
                md_dict = json.load(fr)
            md_dict_intkey = {int(k): v for k, v in md_dict.items()}
            self.md_dict_dump.update(md_dict_intkey)
            self.caseids_sorted = sorted(self.md_dict_dump)

            for case_id, case_md_dict in md_dict_intkey.items():
                md_dict_intkey_verification_class = case_md_dict["verification_class"]

                if (
                    md_dict_intkey_verification_class
                    not in self.verification_item_case_id_mapping
                ):
                    self.verification_item_case_id_mapping[
                        md_dict_intkey_verification_class
                    ] = []

                self.verification_item_case_id_mapping[
                    md_dict_intkey_verification_class
                ].append(case_id)

            self.verification_item_case_id_mapping[
                md_dict_intkey_verification_class
            ].sort()

        self.md_full_string0 = """
# Verification Results:

| Case No.               | Data Source                                | Verification Class | Sample # | Pass # | Fail # | Verification Passed? |
| ---------------------- | ------------------------------------------ | ------------------ | -------- | ------ | ------ | -------------------- |
"""

    def report_multiple_cases(self, item_names: List[str] = []) -> None:
        """Report/summarize multiple verification results.

        Args:
            item_names (List): List of unique verification item names. If the `item_names` argument is empty, all the verification results in the `verification_json` argument are reported.
        """

        # check `item_names` type
        if not isinstance(item_names, List):
            logging.error(
                f"The type of the `item_names` arg needs to be List. It cannot be {type(item_names)}."
            )
            return None

        # collect verification results
        if len(item_names) > 0:
            # when only a selective verification results are read
            for item_name in item_names:
                if item_name not in self.verification_item_case_id_mapping:
                    logging.error(f"{item_name} is not part of the read files.")
                    return None

                for caseid in self.verification_item_case_id_mapping[item_name]:
                    self._result_collector_helper(caseid)
        else:
            # when `item_no` is empty -> all the results are read
            for item_no in self.caseids_sorted:
                self._result_collector_helper(item_no)

        with open(self.result_md_path, "w") as fw:
            fw.write(self.md_full_string0)

    def _result_collector_helper(self, caseid: int) -> None:
        """helper method for the `report_multiple_cases` method.

        Args:
            caseid: id number of the given verification item.
        """

        case_dict = self.md_dict_dump[caseid]
        outcome = case_dict["outcome_notes"]
        model_file = case_dict["model_file"]
        verification_class = case_dict["verification_class"]

        mdtable_row = f"| [{caseid}](./case-{caseid}.md) | {model_file} | {verification_class} | {outcome['Sample #']} | {outcome['Pass #']} | {outcome['Fail #']} | {outcome['Verification Passed?']} |\n"
        self.md_full_string0 += mdtable_row

        md_section = case_dict["md_content"]
        md_section += "[Back](results.md)"
        with open(f"{self.result_md_dir}/case-{caseid}.md", "w") as casew:
            casew.write(md_section)
