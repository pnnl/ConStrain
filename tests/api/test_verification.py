import unittest, sys, os

sys.path.append("./constrain")
from api import VerificationCase
from api import Verification
from api import DataProcessing


class TestVerification(unittest.TestCase):
    cases = [
        {
            "no": 1,
            "run_simulation": False,
            "simulation_IO": {
                "idf": "./tests/api/data/ASHRAE901_OfficeMedium_STD2019_Atlanta.idf",
                "idd": "./resources/Energy+V9_0_1.idd",
                "weather": "./weather/USA_GA_Atlanta-Hartsfield.Jackson.Intl.AP.722190_TMY3.epw",
                "output": "eplusout.csv",
                "ep_path": "C:\\EnergyPlusV9-0-1\\energyplus.exe",
            },
            "expected_result": "pass",
            "datapoints_source": {
                "idf_output_variables": {
                    "o": {
                        "subject": "BLDG_OCC_SCH_WO_SB",
                        "variable": "Schedule Value",
                        "frequency": "TimeStep",
                    },
                    "m_oa": {
                        "subject": "CORE_BOTTOM VAV BOX COMPONENT",
                        "variable": "Zone Air Terminal Outdoor Air Volume Flow Rate",
                        "frequency": "TimeStep",
                    },
                    "m_ea": {
                        "subject": "CORE_MID VAV BOX COMPONENT",
                        "variable": "Zone Air Terminal Outdoor Air Volume Flow Rate",
                        "frequency": "TimeStep",
                    },
                    "eco_onoff": {
                        "subject": "PACU_VAV_BOT",
                        "variable": "Air System Outdoor Air Economizer Status",
                        "frequency": "TimeStep",
                    },
                },
                "parameters": {
                    "tol_o": 0.03,
                    "tol_m_ea": 50,
                    "tol_m_oa": 50,
                },
            },
            "verification_class": "AutomaticOADamperControl",
        },
        {
            "no": 2,
            "run_simulation": False,
            "simulation_IO": {
                "idf": "./tests/api/data/ASHRAE901_OfficeMedium_STD2019_Atlanta.idf",
                "idd": "./resources/Energy+V9_0_1.idd",
                "weather": "./weather/USA_GA_Atlanta-Hartsfield.Jackson.Intl.AP.722190_TMY3.epw",
                "output": "eplusout.csv",
                "ep_path": "C:\\EnergyPlusV9-0-1\\energyplus.exe",
            },
            "expected_result": "pass",
            "datapoints_source": {
                "idf_output_variables": {
                    "o": {
                        "subject": "BLDG_OCC_SCH_WO_SB",
                        "variable": "Schedule Value",
                        "frequency": "TimeStep",
                    },
                    "m_oa": {
                        "subject": "CORE_MID VAV BOX COMPONENT",
                        "variable": "Zone Air Terminal Outdoor Air Volume Flow Rate",
                        "frequency": "TimeStep",
                    },
                    "m_ea": {
                        "subject": "CORE_TOP VAV BOX COMPONENT",
                        "variable": "Zone Air Terminal Outdoor Air Volume Flow Rate",
                        "frequency": "TimeStep",
                    },
                    "eco_onoff": {
                        "subject": "PACU_VAV_MID",
                        "variable": "Air System Outdoor Air Economizer Status",
                        "frequency": "TimeStep",
                    },
                },
                "parameters": {
                    "tol_o": 0.03,
                    "tol_m_ea": 50,
                    "tol_m_oa": 50,
                },
            },
            "verification_class": "AutomaticOADamperControl",
        },
    ]

    def test_constructor(self):
        with self.assertLogs() as logobs:
            # Empty constructor
            v_obj = Verification()
            self.assertEqual(
                "ERROR:root:A VerificationCase object should be provided to `verifications`.",
                logobs.output[0],
            )

            # Cases argument is not a VerificationCase instance
            v_obj = Verification(verifications="cases")
            self.assertEqual(
                "ERROR:root:A VerificationCase should be provided not a <class 'str'>.",
                logobs.output[1],
            )

            # Empty VerificationCase
            vc = VerificationCase(cases=self.cases)
            org_cases = vc.case_suite
            vc.case_suite = {}
            v_obj = Verification(verifications=vc)
            self.assertEqual(
                "ERROR:root:The verification case suite is empty.",
                logobs.output[2],
            )

            # Correct usage
            vc.case_suite = org_cases
            v_obj = Verification(verifications=vc)
            assert len(v_obj.cases) == 2

    def test_configure(self):
        with self.assertLogs() as logobs:
            vc = VerificationCase(cases=self.cases)
            v_obj = Verification(verifications=vc)

            # Valid output_path
            v_obj.configure()
            self.assertEqual(
                "ERROR:root:An output_path argument should be specified.",
                logobs.output[0],
            )
            v_obj.configure(output_path="./test")
            self.assertEqual(
                "ERROR:root:The specificed output directory does not exist.",
                logobs.output[1],
            )

            # Valid lib_items_path
            v_obj.configure(output_path="./")
            self.assertEqual(
                "ERROR:root:A path to the library of verification cases should be provided.",
                logobs.output[2],
            )
            v_obj.configure(output_path="./", lib_items_path=12)
            self.assertEqual(
                "ERROR:root:The path to the library of verification cases is not valid.",
                logobs.output[3],
            )
            v_obj.configure(output_path="./", lib_items_path="./test")
            self.assertEqual(
                "ERROR:root:The path to the library of verification cases is not valid.",
                logobs.output[4],
            )
            v_obj.configure(
                output_path="./", lib_items_path="./resources/Energy+V9_0_1.idd"
            )
            self.assertEqual(
                "ERROR:root:The library should be a JSON file.",
                logobs.output[5],
            )

            # Valid plot_option
            v_obj.configure(
                output_path="./",
                lib_items_path="./schema/library.json",
                plot_option="test",
            )
            self.assertEqual(
                "ERROR:root:The plot_option argument should either be all-compact, all-expand, day-compact, day-expand, or None, not test.",
                logobs.output[6],
            )

            # Valid fig_size
            v_obj.configure(
                output_path="./",
                lib_items_path="./schema/library.json",
                plot_option=None,
                fig_size=("a", 5),
            )
            self.assertEqual(
                "ERROR:root:The fig_size argument should be a tuple of integers or floats.",
                logobs.output[7],
            )
            v_obj.configure(
                output_path="./",
                lib_items_path="./schema/library.json",
                plot_option=None,
                fig_size="test",
            )
            self.assertEqual(
                "ERROR:root:The fig_size argument should be a tuple of integers or floats. Here is the variable type that was passed <class 'str'>.",
                logobs.output[8],
            )

            # Valid num_threads
            v_obj.configure(
                output_path="./",
                lib_items_path="./schema/library.json",
                plot_option=None,
                fig_size=(6, 5),
                num_threads=0,
            )
            self.assertEqual(
                "ERROR:root:The number of threads should be an integer greater than 1.",
                logobs.output[9],
            )

            # Valid preprocessed data
            df = {}
            v_obj.configure(
                output_path="./",
                lib_items_path="./schema/library.json",
                plot_option=None,
                fig_size=(6, 5),
                num_threads=1,
                preprocessed_data=df,
            )
            self.assertEqual(
                "ERROR:root:A Pandas DataFrame should be passed as the `preprocessed_data` argument, not a <class 'dict'>.",
                logobs.output[10],
            )

            # Correct usage
            filep = "./tests/api/data/data_eplus.csv"
            df = DataProcessing(data_path=filep, data_source="EnergyPlus")
            v_obj.configure(
                output_path="./",
                lib_items_path="./schema/library.json",
                plot_option=None,
                fig_size=(6, 5),
                num_threads=1,
                preprocessed_data=df.data,
            )
            assert len(logobs.output) == 11

    def test_run_single_verification(self):
        # Single verification
        vc = VerificationCase(cases=self.cases)
        v_obj = Verification(verifications=vc)
        v_obj.configure(
            output_path="./tests/api",
            lib_items_path="./schema/library.json",
            plot_option=None,
            fig_size=(6, 5),
            num_threads=1,
        )
        v_obj.run_single_verification(case=v_obj.cases[list(v_obj.cases.keys())[0]])
        assert os.path.isfile("./tests/api/1_md.json")

    def test_run_single_verification_wit_preprocessed_data(self):
        # Load verification cases and built verification
        vc = VerificationCase(cases=self.cases)
        v_obj = Verification(verifications=vc)

        # Load pre-processed data
        filep = "./tests/api/data/ASHRAE901_OfficeMedium_STD2019_Atlanta_injected_VerificationNo1/eplusout.csv"
        df = DataProcessing(data_path=filep, data_source="EnergyPlus")
        df.add_parameter(name="tol_o", value=0.03, inplace=True)
        df.add_parameter(name="tol_m_ea", value=50, inplace=True)
        df.add_parameter(name="tol_m_oa", value=50, inplace=True)

        v_obj.configure(
            output_path="./tests/api",
            lib_items_path="./schema/library.json",
            plot_option=None,
            fig_size=(6, 5),
            num_threads=1,
            preprocessed_data=df.data,
        )
        v_obj.run_single_verification(case=v_obj.cases[list(v_obj.cases.keys())[0]])
        assert os.path.isfile("./tests/api/1_md.json")

    def test_run(self):
        # Multiple verification in parallel
        vc = VerificationCase(cases=self.cases)
        v_obj = Verification(verifications=vc)
        v_obj.configure(
            output_path="./tests/api",
            lib_items_path="./schema/library.json",
            plot_option=None,
            fig_size=(6, 5),
            num_threads=2,
        )
        v_obj.run()
        assert os.path.isfile("./tests/api/1_md.json")
        assert os.path.isfile("./tests/api/2_md.json")


if __name__ == "__main__":
    unittest.main()
