import sys
import unittest

import pandas as pd

sys.path.append("./src")
from library.trim_respond_logic import TrimRespondLogic

# data preparation
start_date = "2023-06-21 12:00:00"  # Start date and time
end_date = "2023-06-21 12:59:59"  # End date and time

data = pd.DataFrame(columns=["Date/Time", "setpoint", "number_of_requests"])
timestamps = pd.date_range(start=start_date, end=end_date, freq="2T")
data["Date/Time"] = timestamps
# fmt: off
# The below data is from Figure 5.1.14.4 in the ASHRAE G36-2021
data["setpoint"] = [0.50, 0.46, 0.42, 0.48,0.60, 0.75, 0.81, 0.77, 0.73, 0.69, 0.65, 0.61, 0.57, 0.53, 0.49, 0.45, 0.41, 0.37, 0.33, 0.29, 0.25, 0.21, 0.36, 0.51, 0.66, 0.81, 0.77, 0.73, 0.85, 0.81]
data["number_of_requests"] = [0, 1, 2, 3, 4, 6, 3, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 1, 0, 1, 2, 6, 6, 5, 5, 2, 2, 4, 2]
# fmt: on


class TestTrimRespond(unittest.TestCase):
    def test_check_args_type(self):
        """Test whether arguments' type is correct."""

        # check `data` (type)
        with self.assertLogs() as logobs:
            TrimRespondLogic(
                dict(data),
                Td="0",
                ignored_requests=2,
                SPtrim=-0.04,
                SPres=0.06,
                SPmin=0.15,
                SPmax=1.5,
                SPres_max=0.15,
                tol=0.01,
                controller_type="direct_acting",
            )
            self.assertEqual(
                "ERROR:root:The type of the `df` arg must be a dataframe. It cannot be <class 'dict'>.",
                logobs.output[0],
            )

        # check `data` (missing column)
        with self.assertLogs() as logobs:
            TrimRespondLogic(
                data.drop("setpoint", axis=1),
                Td="0",
                ignored_requests=2,
                SPtrim=-0.04,
                SPres=0.06,
                SPmin=0.15,
                SPmax=1.5,
                SPres_max=0.15,
                tol=0.01,
                controller_type="direct_acting",
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
                SPtrim=-0.04,
                SPres=0.06,
                SPmin=0.15,
                SPmax=1.5,
                SPres_max=0.15,
                tol=0.01,
                controller_type="direct_acting",
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
                SPtrim=-0.04,
                SPres=0.06,
                SPmin=0.15,
                SPmax=1.5,
                SPres_max=0.15,
                tol=0.01,
                controller_type="direct_acting",
            )
            self.assertEqual(
                "ERROR:root:The type of the `ignored_requests` arg must be an int. It cannot be <class 'str'>.",
                logobs.output[0],
            )
        # check `SPtrim`
        with self.assertLogs() as logobs:
            TrimRespondLogic(
                data,
                Td=0,
                ignored_requests=2,
                SPtrim="-0.04",
                SPres=0.06,
                SPmin=0.15,
                SPmax=1.5,
                SPres_max=0.15,
                tol=0.01,
                controller_type="direct_acting",
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
                SPtrim=-0.04,
                SPres="0.06",
                SPmin=0.15,
                SPmax=1.5,
                SPres_max=0.15,
                tol=0.01,
                controller_type="direct_acting",
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
                SPtrim=-0.04,
                SPres=0.06,
                SPmin="0.15",
                SPmax=1.5,
                SPres_max=0.15,
                tol=0.01,
                controller_type="direct_acting",
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
                SPtrim=-0.04,
                SPres=0.06,
                SPmin=0.15,
                SPmax="1.5",
                SPres_max=0.15,
                tol=0.01,
                controller_type="direct_acting",
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
                SPtrim=-0.04,
                SPres=0.06,
                SPmin=0.15,
                SPmax=1.5,
                SPres_max="0.15",
                tol=0.01,
                controller_type="direct_acting",
            )
            self.assertEqual(
                "ERROR:root:The type of the `SPres_max` arg must be a float or int. It cannot be <class 'str'>.",
                logobs.output[0],
            )

        # check `tol`
        with self.assertLogs() as logobs:
            TrimRespondLogic(
                data,
                Td=0,
                ignored_requests=2,
                SPtrim=-0.04,
                SPres=0.06,
                SPmin=0.15,
                SPmax=1.5,
                SPres_max=0.15,
                tol="0.01",
                controller_type="direct_acting",
            )
            self.assertEqual(
                "ERROR:root:The type of the `tol` arg must be a float or int. It cannot be <class 'str'>.",
                logobs.output[0],
            )

        # check `controller_type`
        with self.assertLogs() as logobs:
            TrimRespondLogic(
                data,
                Td=0,
                ignored_requests=2,
                SPtrim=-0.04,
                SPres=0.06,
                SPmin=0.15,
                SPmax=1.5,
                SPres_max=0.15,
                tol=0.01,
                controller_type="wrong_value",
            )
            self.assertEqual(
                "ERROR:root:`controller_type` arg must be either `direct_acting` or `reverse_acting`. It can't be `wrong_value`.",
                logobs.output[0],
            )

    def test_TR_logic_verification(self):
        """test whether the T&R logic was implemented correctly."""

        tr_obj = TrimRespondLogic(
            data,
            Td=0,
            ignored_requests=2,
            SPtrim=-0.04,
            SPres=0.06,
            SPmin=0.15,
            SPmax=1.5,
            SPres_max=0.15,
            tol=0.01,
            controller_type="direct_acting",
        )
        self.assertTrue(all(tr_obj))


if __name__ == "__main__":
    unittest.main()
