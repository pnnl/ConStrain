from unittest import TestCase

import pandas as pd
from constrain.datetimeep import DateTimeEP


class TestDateTimeEP(TestCase):
    def test_datetimeep(self):
        data = {"Date/Time": ["01/01  00:15:00", " 01/01  00:30:00"]}
        df = pd.DataFrame(data)
        df_tsfm = DateTimeEP(df, year=1988).transform()

        self.assertTrue(
            df_tsfm.index[0].year == 1988,
            f"EnergyPlus to datetime conversion is incorrect, year should be 1988 but is {df_tsfm.index[0].year}.",
        )
        self.assertTrue(
            df_tsfm.index[0].month == 1,
            f"EnergyPlus to datetime conversion is incorrect, month should be 1 but is {df_tsfm.index[0].month}.",
        )
        self.assertTrue(
            df_tsfm.index[0].day == 1,
            f"EnergyPlus to datetime conversion is incorrect, day should be 1 but is {df_tsfm.index[0].day}.",
        )
        self.assertTrue(
            df_tsfm.index[0].hour == 0,
            f"EnergyPlus to datetime conversion is incorrect, hour should be 0 but is {df_tsfm.index[0].hour}.",
        )
        self.assertTrue(
            df_tsfm.index[0].minute == 15,
            f"EnergyPlus to datetime conversion is incorrect, minute should be 15 but is {df_tsfm.index[0].minute}.",
        )
        self.assertTrue(
            df_tsfm.index[0].second == 0,
            f"EnergyPlus to datetime conversion is incorrect, second should be 0 but is {df_tsfm.index[0].second}.",
        )
