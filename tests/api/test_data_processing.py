import unittest, sys, datetime, copy

import matplotlib

sys.path.append("./constrain")

from api import DataProcessing


# Helper
def round_equal_dict(a: dict, b: dict, round_digits=2) -> bool:
    """
    Check if two nested dictionaries are the same considering rounding numeric values.
    Two leaf values are considered equal if they are exactly the same or are numerically "round_equal".
    Caution when nested dictionaries contain list of not exactly same elements. This is NOT EQUAL here
    """
    if a == b:  # save the effort if they are exactly the same
        return True

    for (k_a, v_a), (k_b, v_b) in zip(sorted(a.items()), sorted(b.items())):
        if k_a != k_b:  # when keys are not the same
            return False
        if v_a == v_b:
            continue  # save the effort if values are the same (especially when non-numeric)

        if isinstance(v_a, dict) and isinstance(
            v_b, dict
        ):  # recursion when values are dicts
            if not round_equal_dict(v_a, v_b, round_digits):
                return False
            continue
        try:  # in case a non-numeric value still exists here
            if round(v_a, round_digits) != round(
                v_b, round_digits
            ):  # check numeric value
                return False
        except:
            return False
    return True


class TestDataProcessing(unittest.TestCase):
    def test_constructor_empty(self):
        with self.assertLogs() as logobs:
            dp = DataProcessing()
            self.assertEqual(
                "ERROR:root:A `data_path` argument should be provided.",
                logobs.output[0],
            )
            filep = "./tests/api/data/data_complete.csv"
            dp = DataProcessing(data_path=filep)
            self.assertEqual(
                "ERROR:root:A `data_source` argument should be provided.",
                logobs.output[1],
            )

    def test_missing_datafile(self):
        with self.assertLogs() as logobs:
            filep = "./data/missing_file.csv"
            dp = DataProcessing(data_path=filep, data_source="EnergyPlus")
            self.assertEqual(
                f"ERROR:root:The file {filep} does not exists.", logobs.output[0]
            )

    def test_missing_datafile_error(self):
        with self.assertLogs() as logobs:
            filep = "./tests/api/data/data_non_ep_head.csv"
            dp = DataProcessing(data_path=filep, data_source="EnergyPlus")
            self.assertEqual(
                f"ERROR:root:An error occured when opening {filep}. Please make sure that the file can be opened, and/or that it contains the correct headers.",
                logobs.output[0],
            )

    def test_ep_data_file(self):
        filep = "./tests/api/data/data_eplus.csv"
        t = DataProcessing(data_path=filep, data_source="EnergyPlus")
        assert len(t.data) == 2

    def test_other_data_file(self):
        filep = "./tests/api/data/data_non_ep_head.csv"
        dp = DataProcessing(
            data_path=filep, data_source="Other", timestamp_column_name="Date Time"
        )
        assert len(dp.data) == 2

    def test_datafile_error_parsing(self):
        with self.assertLogs() as logobs:
            filep = "./tests/api/data/data_err_parse.csv"
            dp = DataProcessing(
                data_path=filep, data_source="Other", timestamp_column_name="Date/Time"
            )
            self.assertEqual(
                f"ERROR:root:The data in Date/Time could not be converted to Python datetime object. Make sure that the data is consistent defined as a set of date strings.",
                logobs.output[0],
            )

    def test_datafile_missing_datetimecol(self):
        with self.assertLogs() as logobs:
            filep = "./tests/api/data/data_non_ep_head.csv"
            dp = DataProcessing(data_path=filep, data_source="Other")
            self.assertEqual(
                "ERROR:root:timestamp_column_name is required when data_source = 'Other'",
                logobs.output[0],
            )

    def test_datafile_missing_datetimecol(self):
        with self.assertLogs() as logobs:
            filep = "./tests/api/data/data_non_ep_head.csv"
            dp = DataProcessing(data_path=filep, data_source="Make up source")
            self.assertEqual(
                "ERROR:root:data_source = Make up source is not allowed.",
                logobs.output[0],
            )

    def test_slice_add_parameter(self):
        with self.assertLogs() as logobs:
            filep = "./tests/api/data/data_complete.csv"
            dp = DataProcessing(data_path=filep, data_source="EnergyPlus")
            dp.slice("2000-01-01 11:00", "2000-01-01 11:00")
            self.assertEqual(
                f"ERROR:root:The start_time argument is not a Python datetime object.",
                logobs.output[0],
            )
            dp.slice(datetime.datetime(2000, 1, 1, 11), "2000-01-01 11:00")
            self.assertEqual(
                f"ERROR:root:The end_time argument is not a Python datetime object.",
                logobs.output[1],
            )
            dp.add_parameter()
            self.assertEqual(
                f"ERROR:root:A parameter name should be specified.",
                logobs.output[2],
            )
            dp.add_parameter(name="test")
            self.assertEqual(
                f"ERROR:root:A parameter value should be specified.",
                logobs.output[3],
            )
        df_w_param = dp.add_parameter(name="test", value=-999)
        assert "test" in list(df_w_param)
        assert "test" not in dp.data.columns
        dp.add_parameter(name="test", value=-999, inplace=True)
        assert "test" in list(dp.data.columns)
        s = dp.slice(
            datetime.datetime(2000, 1, 1, 11), datetime.datetime(2000, 1, 1, 13)
        )
        assert len(s) == 3
        dp.slice(
            datetime.datetime(2000, 1, 1, 12),
            datetime.datetime(2000, 1, 1, 13),
            inplace=True,
        )
        assert len(dp.data) == 2

        with self.assertLogs() as logobs:
            dp.slice(
                datetime.datetime(2000, 1, 1, 12), datetime.datetime(2000, 1, 1, 11)
            )
            self.assertEqual(
                f"ERROR:root:The end_time cannot be an earlier data than start_time.",
                logobs.output[0],
            )

        with self.assertLogs() as logobs:
            s = dp.slice(
                datetime.datetime(2000, 1, 1, 11), datetime.datetime(2000, 1, 1, 11)
            )
            self.assertEqual(
                f"WARNING:root:Data slice contains no sample.",
                logobs.output[0],
            )

    def test_apply_function(self):
        with self.assertLogs() as logobs:
            filep = "./tests/api/data/data_complete.csv"
            dp = DataProcessing(data_path=filep, data_source="EnergyPlus")
            dp.apply_function()
            self.assertEqual(
                f"ERROR:root:A list of variables was not specified.",
                logobs.output[len(logobs.output) - 1],
            )
            dp.apply_function([])
            self.assertEqual(
                f"ERROR:root:The variable name list is empty.",
                logobs.output[len(logobs.output) - 1],
            )
            dp.apply_function(
                variable_names=[
                    "VariableNotInDataset",
                    "Environment:Site Outdoor Air Drybulb Temperature [C](Hourly)",
                    "CORE_BOTTOM:Zone Air Temperature [C](Hourly)",
                ],
                new_variable_name="subset mean",
                function_to_apply="mean",
            )
            self.assertEqual(
                f"ERROR:root:Variable name(s) {['VariableNotInDataset']} not in the dataset.",
                logobs.output[len(logobs.output) - 1],
            )
            dp.apply_function(variable_names={})
            self.assertEqual(
                f"ERROR:root:A list of variable names should be passed as an argument not a <class 'dict'>.",
                logobs.output[len(logobs.output) - 1],
            )
            dp.apply_function(
                [
                    "Environment:Site Outdoor Air Drybulb Temperature [C](Hourly)",
                    "CORE_BOTTOM:Zone Air Temperature [C](Hourly)",
                ]
            )
            self.assertEqual(
                f"ERROR:root:A new variable name should be provided.",
                logobs.output[len(logobs.output) - 1],
            )
            dp.apply_function(
                [
                    "Environment:Site Outdoor Air Drybulb Temperature [C](Hourly)",
                    "CORE_BOTTOM:Zone Air Temperature [C](Hourly)",
                ],
                "Agg",
                "EXP",
            )
            self.assertEqual(
                f"ERROR:root:The function to apply should be `sum`, `min`, `max`, or `average, not exp.",
                logobs.output[len(logobs.output) - 1],
            )

        assert (
            round(
                dp.apply_function(
                    [
                        "Environment:Site Outdoor Air Drybulb Temperature [C](Hourly)",
                        "CORE_BOTTOM:Zone Air Temperature [C](Hourly)",
                    ],
                    "Agg",
                    "Average",
                )["Agg"].iloc[0],
                2,
            )
            == 10.09
        )
        assert (
            round(
                dp.apply_function(
                    [
                        "Environment:Site Outdoor Air Drybulb Temperature [C](Hourly)",
                        "CORE_BOTTOM:Zone Air Temperature [C](Hourly)",
                    ],
                    "Agg",
                    "min",
                )["Agg"].iloc[0],
                2,
            )
            == 1.65
        )
        assert (
            round(
                dp.apply_function(
                    [
                        "Environment:Site Outdoor Air Drybulb Temperature [C](Hourly)",
                        "CORE_BOTTOM:Zone Air Temperature [C](Hourly)",
                    ],
                    "Agg",
                    "max",
                )["Agg"].iloc[0],
                2,
            )
            == 18.53
        )
        assert (
            round(
                dp.apply_function(
                    [
                        "Environment:Site Outdoor Air Drybulb Temperature [C](Hourly)",
                        "CORE_BOTTOM:Zone Air Temperature [C](Hourly)",
                    ],
                    "Agg",
                    "Sum",
                )["Agg"].iloc[0],
                2,
            )
            == 20.18
        )

    def test_summary(self):
        expected_results = {
            "number_of_data_points": 24,
            "average_resolution_in_second": 3600,
            "variables_summary": {
                "Environment:Site Outdoor Air Drybulb Temperature [C](Hourly)": {
                    "minimum": -4.0,
                    "maximum": 6.25,
                    "mean": 0.7833333333333333,
                    "standard_deviation": 3.3630500376229255,
                },
                "CORE_BOTTOM:Zone Air Temperature [C](Hourly)": {
                    "minimum": 18.27273964,
                    "maximum": 21.00004169,
                    "mean": 19.503968912500003,
                    "standard_deviation": 1.0244291105492493,
                },
                "CORE_MID:Zone Air Temperature [C](Hourly)": {
                    "minimum": 17.24338178,
                    "maximum": 21.00003688,
                    "mean": 19.194468342916668,
                    "standard_deviation": 1.451985874981613,
                },
                "CORE_TOP:Zone Air Temperature [C](Hourly)": {
                    "minimum": 15.59995364,
                    "maximum": 21.00035935,
                    "mean": 18.347906522916666,
                    "standard_deviation": 2.247706588900561,
                },
                "PERIMETER_BOT_ZN_1:Zone Air Temperature [C](Hourly)": {
                    "minimum": 16.76223663,
                    "maximum": 23.64975651,
                    "mean": 19.837477728333337,
                    "standard_deviation": 2.2800476016223246,
                },
                "PERIMETER_MID_ZN_1:Zone Air Temperature [C](Hourly)": {
                    "minimum": 15.60003369,
                    "maximum": 24.00038357,
                    "mean": 19.132399963749997,
                    "standard_deviation": 3.3659979386208,
                },
            },
        }
        filep = "./tests/api/data/data_complete.csv"
        dp = DataProcessing(data_path=filep, data_source="EnergyPlus")
        results = dp.summary()

        flag = round_equal_dict(results, expected_results)
        assert flag

    def test_concatenate(self):
        with self.assertLogs() as logobs:
            filep = "./tests/api/data/data_complete.csv"
            dp = DataProcessing(data_path=filep, data_source="EnergyPlus")
            dp.concatenate()
            self.assertEqual(
                f"ERROR:root:A list of datasets must be provided. The datasets argument that was passed is <class 'NoneType'>.",
                logobs.output[0],
            )
            dp.concatenate([])
            self.assertEqual(
                f"ERROR:root:The list of dataset that was provided is empty.",
                logobs.output[1],
            )
            df_b = dp.slice(
                datetime.datetime(2000, 1, 1, 14), datetime.datetime(2000, 1, 1, 16)
            )
            dp.data = dp.slice(
                datetime.datetime(2000, 1, 1, 11), datetime.datetime(2000, 1, 1, 13)
            )
            datasets_b = [df_b]
            datasets_b_original = [df_b]
            dp.concatenate(datasets=datasets_b, axis=3)
            self.assertEqual(
                f"ERROR:root:The axis argument should either be 1, or 0.",
                logobs.output[2],
            )

            df_c = dp.concatenate(datasets=datasets_b, axis=1)
            assert len(df_c) == 6
            dp.data["test"] = 12.0
            df_d = dp.concatenate(datasets=datasets_b, axis=1)
            self.assertEqual(
                f"ERROR:root:The datasets must contain the same column headers.",
                logobs.output[3],
            )
            assert datasets_b == datasets_b_original

            df_e = copy.deepcopy(dp.data)
            dp.data.drop("test", axis=1, inplace=True)

            datasets_c = [df_c]
            datasets_c_original = [df_c]
            df_f = dp.concatenate(datasets=datasets_c, axis=0)
            assert datasets_c == datasets_c_original
            self.assertEqual(
                f"ERROR:root:The datasets must have the same indexes.",
                logobs.output[4],
            )

            datasets_e = [df_e["test"]]
            datasets_e_original = [df_e["test"]]
            df_g = dp.concatenate(datasets=datasets_e, axis=0)
            assert datasets_e == datasets_e_original
            assert len(df_g) == 3

            org_timestamps = df_e.index
            org_timestamps += datetime.timedelta(days=1)
            df_e.set_index(org_timestamps, inplace=True)
            datasets_e = [df_e["test"]]
            datasets_e_original = [df_e["test"]]
            df_h = dp.concatenate(datasets=datasets_e, axis=0)
            assert datasets_e == datasets_e_original
            self.assertEqual(
                f"ERROR:root:The datasets must have the same indexes.",
                logobs.output[5],
            )

            # vertical concatenation of the same dataset doubles number of rows
            df_i = dp.concatenate(datasets=[dp.data], axis=1, inplace=False)
            assert df_i.shape[0] == dp.data.shape[0] * 2

            # horizontal concatenation of the same dataset doubles number of columns
            df_i = dp.concatenate(datasets=[dp.data], axis=0, inplace=False)
            assert df_i.shape[1] == dp.data.shape[1] * 2

    def test_check(self):
        filep = "./tests/api/data/data_missing_outliers.csv"
        dp = DataProcessing(data_path=filep, data_source="EnergyPlus")
        dp.add_parameter(name="Test Constant", value=0, inplace=True)
        expected_results = {
            "Environment:Site Outdoor Air Drybulb Temperature [C](Hourly)": {
                "number_of_missing_values": 1,
                "outliers": 150.0,
            },
            "CORE_BOTTOM:Zone Air Temperature [C](Hourly)": {
                "number_of_missing_values": 2,
                "outliers": None,
            },
            "CORE_MID:Zone Air Temperature [C](Hourly)": {
                "number_of_missing_values": 3,
                "outliers": None,
            },
            "CORE_TOP:Zone Air Temperature [C](Hourly)": {
                "number_of_missing_values": 0,
                "outliers": 53.0,
            },
            "PERIMETER_BOT_ZN_1:Zone Air Temperature [C](Hourly)": {
                "number_of_missing_values": 0,
                "outliers": None,
            },
            "PERIMETER_MID_ZN_1:Zone Air Temperature [C](Hourly)": {
                "number_of_missing_values": 0,
                "outliers": 250.0,
            },
            "Test Constant": {
                "number_of_missing_values": 0,
                "outliers": None,
            },
        }

        results = dp.check()
        for c in list(dp.data.columns):
            assert (
                expected_results[c]["number_of_missing_values"]
                == results[c]["number_of_missing_values"]
            )
            if results[c]["outliers"] is None:
                assert expected_results[c]["outliers"] == results[c]["outliers"]
            else:
                assert (
                    expected_results[c]["outliers"] == results[c]["outliers"].values[0]
                )

    def test_fill_missing_values(self):
        with self.assertLogs() as logobs:
            filep = "./tests/api/data/data_missing_outliers.csv"
            dp = DataProcessing(data_path=filep, data_source="EnergyPlus")
            dp.fill_missing_values()
            self.assertEqual(
                f"ERROR:root:The method should either be linear or bad but not None.",
                logobs.output[0],
            )
            dp.fill_missing_values(method="wrong_method")
            self.assertEqual(
                f"ERROR:root:The method should either be linear or bad but not wrong_method.",
                logobs.output[1],
            )
            dp.fill_missing_values(method="linear", variable_names="variable 1")
            self.assertEqual(
                f"ERROR:root:A list of variable names must be provided. The variables_name argument that was passed is <class 'str'>.",
                logobs.output[2],
            )

            incorrect_vars = list(dp.data.columns)
            incorrect_vars[1] = "wrong var name"
            dp.fill_missing_values(method="pad", variable_names=incorrect_vars)
            self.assertEqual(
                f"ERROR:root:Variable(s) {['wrong var name']} not included in the data.",
                logobs.output[3],
            )

        # fill some missing data
        var_names = list(dp.data.columns)[:2]
        assert dp.data[var_names].isnull().sum().sum() > 0
        filled_df = dp.fill_missing_values(
            method="pad", variable_names=var_names, inplace=False
        )
        assert filled_df[var_names].isnull().sum().sum() == 0
        assert dp.data[var_names].isnull().sum().sum() > 0

        # fill all missing data
        filled_df = dp.fill_missing_values(method="linear", variable_names=[])
        assert filled_df.isnull().sum().sum() == 0
        assert dp.data.isnull().sum().sum() > 0

        assert (
            dp.check()["Environment:Site Outdoor Air Drybulb Temperature [C](Hourly)"][
                "number_of_missing_values"
            ]
            > 0
        )
        filled_df = dp.fill_missing_values(
            method="pad",
            variable_names=[
                "Environment:Site Outdoor Air Drybulb Temperature [C](Hourly)"
            ],
            inplace=False,
        )
        assert (
            dp.check()["Environment:Site Outdoor Air Drybulb Temperature [C](Hourly)"][
                "number_of_missing_values"
            ]
            > 0
        )
        assert (
            filled_df["Environment:Site Outdoor Air Drybulb Temperature [C](Hourly)"]
            .isnull()
            .sum()
            == 0
        )
        dp.fill_missing_values(
            method="linear",
            variable_names=[
                "Environment:Site Outdoor Air Drybulb Temperature [C](Hourly)"
            ],
            inplace=True,
        )
        assert (
            dp.check()["Environment:Site Outdoor Air Drybulb Temperature [C](Hourly)"][
                "number_of_missing_values"
            ]
            == 0
        )

    def test_plot(self):
        with self.assertLogs() as logobs:
            filep = "./tests/api/data/data_complete.csv"
            dp = DataProcessing(data_path=filep, data_source="EnergyPlus")
            dp.plot()
            self.assertEqual(
                f"ERROR:root:A list of variable names must be provided. The variables_name argument that was passed is <class 'NoneType'>.",
                logobs.output[0],
            )
            dp.plot([])
            self.assertEqual(
                f"ERROR:root:The list of variable names that was provided is empty.",
                logobs.output[1],
            )
            dp.plot(
                variable_names=[
                    "Environment:Site Outdoor Air Drybulb Temperature [C](Hourly)",
                    "CORE_BOTTOM:Zone Air Temperature [C](Hourly)",
                    "CORE_MID:Zone Air Temperature [C](Hourly)",
                ]
            )
            self.assertEqual(
                f"ERROR:root:The kind of plot should be either timeseries or scatter but not None.",
                logobs.output[2],
            )
            dp.plot(variable_names=["wrong_variable"], kind="scatter")
            self.assertEqual(
                f"WARNING:root:wrong_variable is not included in the data.",
                logobs.output[3],
            )
            self.assertEqual(
                f"ERROR:root:None of the specified variables were found in data, the plot cannot be generated.",
                logobs.output[4],
            )
            dp.plot(
                variable_names=[
                    "Environment:Site Outdoor Air Drybulb Temperature [C](Hourly)"
                ],
                kind="scatter",
            )
            self.assertEqual(
                f"ERROR:root:A scatter plot requires at least two variables.",
                logobs.output[5],
            )

            varnames = list(dp.data.columns)
            assert isinstance(
                dp.plot(variable_names=varnames[:3], kind="scatter"),
                matplotlib.axes.Axes,
            )
            assert isinstance(
                dp.plot(variable_names=varnames, kind="timeseries"),
                matplotlib.axes.Axes,
            )

    def test_downsampling(self):
        with self.assertLogs() as logobs:
            filep = "./tests/api/data/data_missing_outliers.csv"
            dp = DataProcessing(data_path=filep, data_source="EnergyPlus")
            dp.downsample()
            self.assertEqual(
                f"ERROR:root:A frequency_type argument must be provided.",
                logobs.output[0],
            )
            dp.downsample("X")
            self.assertEqual(
                f"ERROR:root:X is not supported, please choose one of these: dict_keys(['day', 'hour', 'minute', 'second']).",
                logobs.output[1],
            )
            dp.downsample("day")
            self.assertEqual(
                f"ERROR:root:The number of periods should be specified as an integer, not <class 'NoneType'>.",
                logobs.output[2],
            )
            dp.downsample("day", "a")
            self.assertEqual(
                f"ERROR:root:The number of periods should be specified as an integer, not <class 'str'>.",
                logobs.output[3],
            )
            dp.downsample("day", 0)
            self.assertEqual(
                f"ERROR:root:The number of periods should at least be 1.",
                logobs.output[4],
            )
            dp.downsample("day", 2)
            self.assertEqual(
                f"INFO:root:Downsampling will be generated by applying the mean to each variable.",
                logobs.output[5],
            )
            dp.downsample("day", 2, "wrong")
            self.assertEqual(
                f"ERROR:root:The sampling function should be either 'mean' or 'sum'.",
                logobs.output[6],
            )
            assert len(dp.downsample("day", 2, "mean")) == 1
            assert (
                round(
                    dp.downsample("day", 2, "mean")[
                        "Environment:Site Outdoor Air Drybulb Temperature [C](Hourly)"
                    ].values[0],
                    2,
                )
                == 7.24
            )
            assert (
                round(
                    dp.downsample("day", 2, "sum")[
                        "Environment:Site Outdoor Air Drybulb Temperature [C](Hourly)"
                    ].values[0],
                    2,
                )
                == 166.45
            )
            dp.downsample("second", 2, "mean")
            self.assertEqual(
                f"ERROR:root:You are not attempting to 'upsample': The frequency time chosen is lower than the average timestamp resolution.",
                logobs.output[-1],
            )
            dp.downsample("day", 2, {})
            self.assertEqual(
                f"ERROR:root:The dictionary passed as the sample_function argument cannot be empty.",
                logobs.output[-1],
            )
            dp.downsample(
                "day",
                2,
                {
                    "Environment:Site Outdoor Air Drybulb Temperature [C](Hourly)": "mean"
                },
            )
            self.assertEqual(
                f"ERROR:root:CORE_BOTTOM:Zone Air Temperature [C](Hourly) is not in the sampling function dictionary. All variables should be included.",
                logobs.output[-1],
            )
            dp.downsample("day", 2, {"variable that doesnt exist": "mean"})
            self.assertEqual(
                f"ERROR:root:variable that doesnt exist is not in data, downsampling cannot be performed.",
                logobs.output[-1],
            )
            sampling_function = {}
            for v in list(dp.data.columns):
                sampling_function[v] = "exp"
            dp.downsample("day", 2, sampling_function)
            self.assertEqual(
                f"ERROR:root:The sampling function for Environment:Site Outdoor Air Drybulb Temperature [C](Hourly) should be either 'mean' or 'sum'.",
                logobs.output[-1],
            )
            for v in list(dp.data.columns):
                sampling_function[v] = "mean"
            sampling_function["CORE_BOTTOM:Zone Air Temperature [C](Hourly)"] = "sum"
            t = dp.downsample("day", 2, sampling_function)
            assert (
                round(t["CORE_BOTTOM:Zone Air Temperature [C](Hourly)"].values[0], 2)
                == 429.49
            )
            assert (
                round(
                    t[
                        "Environment:Site Outdoor Air Drybulb Temperature [C](Hourly)"
                    ].values[0],
                    2,
                )
                == 7.24
            )


if __name__ == "__main__":
    unittest.main()
