"""
verification.py
====================================
Verification API
"""

import sys, logging, multiprocessing, os
import pandas as pd

from typing import Dict, List, Tuple, Union

sys.path.append("..")

from .verification_case import *
from constrain.run_verification_case import *
from constrain.workflowsteps import *
from constrain.libcases import *


class Verification:
    def __init__(self, verifications: VerificationCase = None):
        self.cases = None
        self.output_path = None
        self.lib_items_path = None
        self.plot_option = None
        self.fig_size = None
        self.num_threads = None

        if verifications is None:
            logging.error(
                "A VerificationCase object should be provided to `verifications`."
            )
        else:
            if isinstance(verifications, VerificationCase):
                if len(verifications.case_suite) == 0:
                    logging.error("The verification case suite is empty.")
                    return None
                else:
                    self.cases = verifications.case_suite
            else:
                logging.error(
                    f"A VerificationCase should be provided not a {type(verifications)}."
                )
                return None

    def configure(
        self,
        output_path: str = None,
        lib_items_path: str = None,
        plot_option: str = None,
        fig_size: tuple = (6.4, 4.8),
        num_threads: int = 1,
        preprocessed_data: pd.DataFrame = None,
    ) -> None:
        """Configure verification environment.

        Args:
            output_path (str): Verification results output path.
            lib_items_path (str): Verification library path (include name of the file with extension).
            plot_option (str, optional): Type of plots to include. It should either be all-compact, all-expand, day-compact, or day-expand. It can also be None, which will plot all types. Default to None.
            fig_size (tuple, optional): Tuple of integers (length, height) describing the size of the figure to plot. Defaults to (6.4, 4.8).
            num_threads (int, optional): Number of threads to run verifications in parallel. Defaults to 1.
            preprocessed_data (pd.DataFrame, optional): Pre-processed data stored in the data frame. Default to None.
        """
        if self.cases is None or len(self.cases) == 0:
            logging.error(
                "The verification case suite is empty, there is nothing to configure."
            )
            return None
        if output_path is None:
            logging.error("An output_path argument should be specified.")
            return None
        elif not os.path.isdir(output_path):
            logging.error("The specificed output directory does not exist.")
            return None

        if lib_items_path is None:
            logging.error(
                "A path to the library of verification cases should be provided."
            )
            return None
        elif not isinstance(lib_items_path, str):
            logging.error("The path to the library of verification cases is not valid.")
            return None
        elif not os.path.isfile(lib_items_path):
            logging.error("The path to the library of verification cases is not valid.")
            return None
        elif "json" != lib_items_path.split(".")[-1].lower():
            logging.error("The library should be a JSON file.")
            return None

        if not plot_option in [
            None,
            "all-compact",
            "all-expand",
            "day-compact",
            "day-expand",
        ]:
            logging.error(
                f"The plot_option argument should either be all-compact, all-expand, day-compact, day-expand, or None, not {plot_option}."
            )
            return None

        if isinstance(fig_size, tuple):
            if not (
                (isinstance(fig_size[0], int) or isinstance(fig_size[0], float))
                and (isinstance(fig_size[1], int) or isinstance(fig_size[1], float))
            ):
                logging.error(
                    "The fig_size argument should be a tuple of integers or floats."
                )
                return None
        else:
            logging.error(
                f"The fig_size argument should be a tuple of integers or floats. Here is the variable type that was passed {type(fig_size)}."
            )
            return None

        if (isinstance(num_threads, int) and num_threads < 1) or (
            not isinstance(num_threads, int)
        ):
            logging.error("The number of threads should be an integer greater than 1.")
            return None

        if (
            not isinstance(preprocessed_data, pd.DataFrame)
            and not preprocessed_data is None
        ):
            logging.error(
                f"A Pandas DataFrame should be passed as the `preprocessed_data` argument, not a {type(preprocessed_data)}."
            )
            return None

        self.output_path = output_path
        self.lib_items_path = lib_items_path
        self.plot_option = plot_option
        self.fig_size = fig_size
        self.num_threads = num_threads
        self.preprocessed_data = preprocessed_data

    def run_single_verification(self, case: dict = None) -> None:
        """Run a single verification and generate a json file containing markdown report string and other results info.

        Args:
            case (dict): Verification case dictionary.
        """
        # Input validation
        if case is None:
            logging.error("A case must be passed as an argument.")

        if not isinstance(case, dict):
            logging.error(
                f"A case dictionary must be passed as an argument, not a {type(case)}."
            )

        # Run verification
        items = assemble_verification_items(
            cases=case, lib_items_path=self.lib_items_path
        )
        results = run_libcase(
            item_dict=items[0],
            plot_option=self.plot_option,
            output_path=self.output_path,
            fig_size=self.fig_size,
            produce_outputs=True,
            preprocessed_data=self.preprocessed_data,
        )

        # TODO: JXL to make this compatible with reporting API, save md json instead of md files directly.
        # Output case summary
        cases_file = f"{self.output_path}/{case['no']}_md.json"
        with open(cases_file, "w") as fw:
            json.dump(results, fw)

    def run(self) -> None:
        """Run all verification cases and generate json files containing results of all cases"""
        # Input validation
        if self.output_path is None:
            self.output_path = ""
        if self.cases is None or len(self.cases) == 0:
            logging.error(
                "The verification case suite is empty, there is nothing to run."
            )
            return None

        # Run verifications
        # with multiprocessing.Pool(self.num_threads) as c:
        #     c.map(self.run_single_verification, self.cases.values())
        for case in self.cases.values():
            self.run_single_verification(case)
