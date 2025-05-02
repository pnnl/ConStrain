import sys
import unittest

import pandas as pd

sys.path.append("./constrain")
from lib_unit_test_runner import *
from library import *

# data preparation
start_date = "2023-06-21 12:00:00"  # Start date and time
end_date = "2023-06-21 12:59:59"  # End date and time

data = pd.DataFrame(
    columns=["setpoint", "number_of_requests"],
    index=pd.date_range(start=start_date, end=end_date, freq="2min"),
)
# fmt: off
# The below data is from Figure 5.1.14.4 in the ASHRAE G36-2021
values_in_inches = [0.50, 0.46, 0.42, 0.48,0.60, 0.75, 0.81, 0.77, 0.73, 0.69, 0.65, 0.61, 0.57, 0.53, 0.49, 0.45, 0.41, 0.37, 0.33, 0.29, 0.25, 0.21, 0.36, 0.51, 0.66, 0.81, 0.77, 0.73, 0.85, 0.81]

# Define the conversion factor
in_to_pa = 248.84

# Convert to Pascals
data["setpoint"]  = [value * in_to_pa for value in values_in_inches]
data["number_of_requests"] = [0, 1, 2, 3, 4, 6, 3, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 1, 0, 1, 2, 6, 6, 5, 5, 2, 2, 4, 2]
data["flag_device"] = [1 for _ in range(30)]
# fmt: on


class TestTrimRespond(unittest.TestCase):
    def test_check_args_type(self):
        """Test whether arguments' type is correct."""

        # check `data` (type)
        with self.assertLogs() as logobs:
            TrimRespondLogic(
                dict(data),
                Td=0,
                ignored_requests=2,
                SP0=120,
                SPtrim=-10,
                SPres=15,
                SPmin=37,
                SPmax=370,
                SPres_max=37,
                controller_type="direct_acting",
                variable_type="pressure",
                variable_subtype="static",
            )
            self.assertEqual(
                "ERROR:root:The type of the `df` arg must be a dataframe. It cannot be <class 'dict'>.",
                logobs.output[0],
            )

        # check `data` index type
        with self.assertLogs() as logobs:
            TrimRespondLogic(
                data.reset_index(drop=True),
                Td=0,
                ignored_requests=2,
                SP0=0.5,
                SPtrim=-0.04,
                SPres=0.06,
                SPmin=0.15,
                SPmax=1.5,
                SPres_max=0.15,
                controller_type="direct_acting",
                variable_type="pressure",
                variable_subtype="static",
            )
            self.assertEqual(
                "ERROR:root:Index's format is not in datetime format.",
                logobs.output[0],
            )

        # check `data` (missing column)
        with self.assertLogs() as logobs:
            TrimRespondLogic(
                data.drop("setpoint", axis=1),
                Td=0,
                ignored_requests=2,
                SP0=120,
                SPtrim=-10,
                SPres=15,
                SPmin=37,
                SPmax=370,
                SPres_max=37,
                controller_type="direct_acting",
                variable_type="pressure",
                variable_subtype="static",
            )
            self.assertEqual(
                "ERROR:root:setpoint column doesn't exist in the `df`.",
                logobs.output[0],
            )

        # check `Td`
        with self.assertLogs() as logobs:
            TrimRespondLogic(
                data,
                Td="0",
                ignored_requests=2,
                SP0=120,
                SPtrim=-10,
                SPres=15,
                SPmin=37,
                SPmax=370,
                SPres_max=37,
                controller_type="direct_acting",
                variable_type="pressure",
                variable_subtype="static",
            )
            self.assertEqual(
                "ERROR:root:The type of the `Td` arg must be a float or int. It cannot be <class 'str'>.",
                logobs.output[0],
            )

        # check `I`
        with self.assertLogs() as logobs:
            TrimRespondLogic(
                data,
                Td=0,
                ignored_requests="2",
                SP0=120,
                SPtrim=-10,
                SPres=15,
                SPmin=37,
                SPmax=370,
                SPres_max=37,
                controller_type="direct_acting",
                variable_type="pressure",
                variable_subtype="static",
            )
            self.assertEqual(
                "ERROR:root:The type of the `ignored_requests` arg must be an int. It cannot be <class 'str'>.",
                logobs.output[0],
            )

        # check `SP0`
        with self.assertLogs() as logobs:
            TrimRespondLogic(
                data,
                Td=0,
                ignored_requests=2,
                SP0="120",
                SPtrim=-10,
                SPres=15,
                SPmin=37,
                SPmax=370,
                SPres_max=37,
                controller_type="direct_acting",
                variable_type="pressure",
                variable_subtype="static",
            )
            self.assertEqual(
                "ERROR:root:The type of the `SP0` arg must be a float or int. It cannot be <class 'str'>.",
                logobs.output[0],
            )

        # check `SPtrim`
        with self.assertLogs() as logobs:
            TrimRespondLogic(
                data,
                Td=0,
                ignored_requests=2,
                SP0=120,
                SPtrim="-10",
                SPres=15,
                SPmin=37,
                SPmax=370,
                SPres_max=37,
                controller_type="direct_acting",
                variable_type="pressure",
                variable_subtype="static",
            )
            self.assertEqual(
                "ERROR:root:The type of the `SPtrim` arg must be a float or int. It cannot be <class 'str'>.",
                logobs.output[0],
            )

        # check `SPres`
        with self.assertLogs() as logobs:
            TrimRespondLogic(
                data,
                Td=0,
                ignored_requests=2,
                SP0=120,
                SPtrim=-10,
                SPres="15",
                SPmin=37,
                SPmax=370,
                SPres_max=37,
                controller_type="direct_acting",
                variable_type="pressure",
                variable_subtype="static",
            )
            self.assertEqual(
                "ERROR:root:The type of the `SPres` arg must be a float or int. It cannot be <class 'str'>.",
                logobs.output[0],
            )

        # check `SPmin`
        with self.assertLogs() as logobs:
            TrimRespondLogic(
                data,
                Td=0,
                ignored_requests=2,
                SP0=120,
                SPtrim=-10,
                SPres=15,
                SPmin="37",
                SPmax=370,
                SPres_max=37,
                controller_type="direct_acting",
                variable_type="pressure",
                variable_subtype="static",
            )
            self.assertEqual(
                "ERROR:root:The type of the `SPmin` arg must be a float or int. It cannot be <class 'str'>.",
                logobs.output[0],
            )

        # check `SPmax`
        with self.assertLogs() as logobs:
            TrimRespondLogic(
                data,
                Td=0,
                ignored_requests=2,
                SP0=120,
                SPtrim=-10,
                SPres=15,
                SPmin=37,
                SPmax="370",
                SPres_max=37,
                controller_type="direct_acting",
                variable_type="pressure",
                variable_subtype="static",
            )
            self.assertEqual(
                "ERROR:root:The type of the `SPmax` arg must be a float or int. It cannot be <class 'str'>.",
                logobs.output[0],
            )

        # check `SPres_max`
        with self.assertLogs() as logobs:
            TrimRespondLogic(
                data,
                Td=0,
                ignored_requests=2,
                SP0=120,
                SPtrim=-10,
                SPres=15,
                SPmin=37,
                SPmax=370,
                SPres_max="37",
                controller_type="direct_acting",
                variable_type="pressure",
                variable_subtype="static",
            )
            self.assertEqual(
                "ERROR:root:The type of the `SPres_max` arg must be a float or int. It cannot be <class 'str'>.",
                logobs.output[0],
            )

        # check `controller_type`
        with self.assertLogs() as logobs:
            TrimRespondLogic(
                data,
                Td=0,
                ignored_requests=2,
                SP0=120,
                SPtrim=-10,
                SPres=15,
                SPmin=37,
                SPmax=370,
                SPres_max=37,
                controller_type="wrong_value",
                variable_type="pressure",
                variable_subtype="static",
            )
            self.assertEqual(
                "ERROR:root:The `controller_type` arg must be either `direct_acting` or `reverse_acting`. It can't be `wrong_value`.",
                logobs.output[0],
            )

        # Check if variable_type has one of the ("temperature", "airflow", "waterflow", "pressure") values
        with self.assertLogs() as logobs:
            TrimRespondLogic(
                data,
                Td=0,
                ignored_requests=2,
                SP0=120,
                SPtrim=-10,
                SPres=15,
                SPmin=37,
                SPmax=370,
                SPres_max=37,
                controller_type="direct_acting",
                variable_type="wrong_var",
                variable_subtype="static",
            )
            self.assertEqual(
                "ERROR:root:The `variable_type` arg must be one of temperature, airflow, waterflow, pressure. It can't be `wrong_var`.",
                logobs.output[0],
            )

        # Check if variable_subtype has a right subtype
        with self.assertLogs() as logobs:
            TrimRespondLogic(
                data,
                Td=0,
                ignored_requests=2,
                SP0=120,
                SPtrim=-10,
                SPres=15,
                SPmin=37,
                SPmax=370,
                SPres_max=37,
                controller_type="direct_acting",
                variable_type="temperature",
                variable_subtype="no_subtype",
            )
            self.assertEqual(
                "ERROR:root:The `variable_subtype` arg doesn't have a right subtype. Please check the ./constrain/tolerances.json file.",
                logobs.output[0],
            )

    def test_TR_logic_verification(self):
        """test whether the T&R logic was implemented correctly."""

        # verify the verification was implemented correctly
        tr_obj = TrimRespondLogic(
            data,
            Td=0,
            ignored_requests=2,
            SP0=120,
            SPtrim=-10,
            SPres=15,
            SPmin=37,
            SPmax=370,
            SPres_max=37,
            controller_type="direct_acting",
            variable_type="pressure",
            variable_subtype="static",
        )

        # check if all verification passed
        self.assertTrue(all(tr_obj["verification"]))

    def test_TR_winter_day_reset(self):
        """Test winter day reset dataset from Modelica"""

        start_date = "2023-12-21 12:00:00"
        modelica_winter = pd.DataFrame(
            columns=["setpoint", "number_of_requests"],
            index=pd.date_range(start=start_date, periods=1441, freq="min"),
        )

        modelica_winter["setpoint"] = (
            [120] * 295
            + [108] * 3
            + [96] * 2
            + [99] * 2
            + [119] * 2
            + [139] * 2
            + [159] * 2
            + [179] * 2
            + [199] * 2
            + [219] * 2
            + [222] * 2
            + [210] * 2
            + [198] * 2
            + [186] * 2
            + [174] * 2
            + [162] * 2
            + [150] * 2
            + [138] * 2
            + [126] * 2
            + [114] * 2
            + [102] * 2
            + [90] * 2
            + [78] * 2
            + [66] * 2
            + [54] * 2
            + [42] * 2
            + [30] * 2
            + [25] * 792
            + [120] * 301
        )
        modelica_winter["number_of_requests"] = (
            [0] * 300
            + [3] * 1
            + [9] * 9
            + [8] * 2
            + [6] * 2
            + [3] * 2
            + [1] * 2
            + [0] * 1123
        )
        modelica_winter["flag_device"] = [0] * 283 + [1] * 857 + [0] * 301

        # verify the verification was implemented correctly
        tr_obj = TrimRespondLogic(
            modelica_winter,
            Td=10,  # 10 mins
            ignored_requests=2,
            SP0=120,
            SPtrim=-12,
            SPres=15,
            SPmin=25,
            SPmax=1000,
            SPres_max=32,
            controller_type="direct_acting",
            variable_type="pressure",
            variable_subtype="static",
        )

        # check if all verification passed
        self.assertTrue(all(tr_obj["verification"]))

    def test_TR_summer_day_reset(self):
        """Test summer day reset dataset from Modelica"""

        start_date = "2023-06-21 12:00:00"
        modelica_summer = pd.DataFrame(
            columns=["setpoint", "number_of_requests", "flag_device"],
            index=pd.date_range(start=start_date, periods=1441, freq="min"),
        )

        modelica_summer["setpoint"] = (
            [120] * 372
            + [108] * 2
            + [96] * 2
            + [84] * 2
            + [72] * 2
            + [60] * 2
            + [48] * 2
            + [36] * 2
            + [25] * 754
            + [120] * 301
        )
        modelica_summer["number_of_requests"] = [0] * 1441
        modelica_summer["flag_device"] = [0] * 360 + [1] * 780 + [0] * 301

        # verify the verification was implemented correctly
        tr_obj = TrimRespondLogic(
            modelica_summer,
            Td=10,
            ignored_requests=2,
            SP0=120,
            SPtrim=-12,
            SPres=15,
            SPmin=25,
            SPmax=1000,
            SPres_max=32,
            controller_type="direct_acting",
            variable_type="pressure",
            variable_subtype="static",
        )

        # check if all verification passed
        self.assertTrue(all(tr_obj["verification"]))


if __name__ == "__main__":
    unittest.main()
