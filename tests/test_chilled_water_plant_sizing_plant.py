import datetime
import sys
import os
import pytest

sys.path.append("./constrain")
import pandas as pd
from lib_unit_test_runner import *
from library import *


def test_chilled_water_plant_sizing_plant_pass():
    # Get sample data from CSV
    csv_path = f"{os.path.dirname(os.path.abspath(__file__))}/api/data/chilled_water_plant_sizing.csv"
    df = pd.read_csv(csv_path)

    # Create datetime index
    start_datetime = "2023-10-01 00:00"
    periods = 525600  # One year of minute data
    minute_index = pd.date_range(start=start_datetime, periods=periods, freq="T")
    df.index = minute_index

    # Drop the Date/Time column if it exists
    if "Date/Time" in df.columns:
        df.drop("Date/Time", axis=1, inplace=True)

    # Perform verification using run_test_verification_with_data
    verification_obj = run_test_verification_with_data(
        "ChilledWaterPlantSizingWholePlant", df
    )

    # Check results
    results = pd.Series(list(verification_obj.result))
    assert results.all()


def test_chilled_water_plant_sizing_plant_fail():
    # Get sample data from CSV
    csv_path = f"{os.path.dirname(os.path.abspath(__file__))}/api/data/chilled_water_plant_sizing.csv"
    df = pd.read_csv(csv_path)
    df["capacity_nominal_plant_water_chilled"] = 1812231.335 * 2 / 1.15

    # Create datetime index
    start_datetime = "2023-10-01 00:00"
    periods = 525600  # One year of minute data
    minute_index = pd.date_range(start=start_datetime, periods=periods, freq="T")
    df.index = minute_index

    # Drop the Date/Time column if it exists
    if "Date/Time" in df.columns:
        df.drop("Date/Time", axis=1, inplace=True)

    # Perform verification using run_test_verification_with_data
    verification_obj = run_test_verification_with_data(
        "ChilledWaterPlantSizingWholePlant", df
    )

    # Check results
    results = pd.Series(list(verification_obj.result))
    assert ~results.any()


def test_chilled_water_plant_sizing_plant_untested():
    # Get sample data from CSV
    csv_path = f"{os.path.dirname(os.path.abspath(__file__))}/api/data/chilled_water_plant_sizing.csv"
    df = pd.read_csv(csv_path)
    df["capacity_nominal_plant_water_chilled"] = 1812231.335 * 2 / 1.15
    df["load_plant_water_chilled"][:300000] = 0

    # Create datetime index
    start_datetime = "2023-10-01 00:00"
    periods = 525600  # One year of minute data
    minute_index = pd.date_range(start=start_datetime, periods=periods, freq="T")
    df.index = minute_index

    # Drop the Date/Time column if it exists
    if "Date/Time" in df.columns:
        df.drop("Date/Time", axis=1, inplace=True)

    # Perform verification using run_test_verification_with_data
    verification_obj = run_test_verification_with_data(
        "ChilledWaterPlantSizingWholePlant", df
    )

    # Check results
    results = pd.Series(list(verification_obj.result))
    assert (results == "Untested").all()
