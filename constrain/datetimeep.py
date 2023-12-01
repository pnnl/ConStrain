import pandas as pd
import datetime


class DateTimeEP:
    """convert EnergyPlus date time string to python datetime"""

    def __init__(self, epdf: pd.DataFrame, year=2000):
        self.year = year
        self.df = epdf.copy(deep=True)

    def transform(self) -> pd.DataFrame:
        dt_list = []
        for i, row in self.df.iterrows():
            dt_list.append(self.epstr2dt(row["Date/Time"]))
        self.df.index = dt_list

        return self.df

    def epstr2dt(self, string: str) -> datetime.datetime:
        """The ep date string has the format: "01/01  00:40:00" """
        strtup = string.strip().split(sep="  ")
        midnight = False
        if strtup[1] == "24:00:00":
            strtup[1] = "00:00:00"
            midnight = True
        dt = datetime.datetime.strptime(
            f"{strtup[0]}/{self.year}  {strtup[1]}", "%m/%d/%Y  %H:%M:%S"
        )
        if midnight:
            dt = dt + datetime.timedelta(days=1)

        return dt
