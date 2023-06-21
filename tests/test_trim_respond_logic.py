import sys
import unittest

import pandas as pd

sys.path.append("./src")
from library.trim_respond_logic import TrimRespondLogic

# data preparation
start_date = "2023-06-21 12:00:00"  # Start date and time
end_date = "2023-06-21 12:59:59"  # End date and time

data = pd.DataFrame(columns=["Date/Time", "static_setpoint", "number_of_requests"])
timestamps = pd.date_range(start=start_date, end=end_date, freq="2T")
data["Date/Time"] = timestamps
# fmt: off
data["static_setpoint"] = [0.50, 0.46, 0.42, 0.48,0.60, 0.75, 0.81, 0.77, 0.73, 0.69, 0.65, 0.61, 0.57, 0.53, 0.49, 0.45, 0.41, 0.37, 0.33, 0.29, 0.25, 0.21, 0.36, 0.51, 0.66, 0.81, 0.77, 0.73, 0.85, 0.81]
data["number_of_requests"] = [0, 1, 2, 3, 4, 6, 3, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 1, 0, 1, 2, 6, 6, 5, 5, 2, 2, 4, 2]
# fmt: on


class TestTrimRespond(unittest.TestCase):
    def test_direct_acting(self):
        result = TrimRespondLogic(
            data,
            setpoint_name="static_setpoint",
            Td=0,
            I=2,
            SPtrim=-0.04,
            SPres=0.06,
            SPmin=0.15,
            SPmax=1.5,
            SPres_max=0.15,
            tol=0.01,
            controller_type="direct_acting",
        )
        self.assertTrue(all(result))


if __name__ == "__main__":
    unittest.main()
