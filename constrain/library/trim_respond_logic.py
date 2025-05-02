import json
import logging
from pathlib import Path
from typing import Union

import pandas as pd
from pandas.api.types import is_datetime64_any_dtype

VARIABLE_SET = ("temperature", "airflow", "waterflow", "pressure")
VARIABLE_SUBTYPE_SET = {
    "temperature": (
        "supply_air",
        "zone",
        "outdoor_air",
        "discharge_air",
        "return_air",
        "general",
    ),
    "airflow": ("supply", "outdoor_air", "exhaust_air", "general"),
    "waterflow": ("hot", "general"),
    "pressure": ("static", "building", "general"),
}


def TrimRespondLogic(
    df: pd.DataFrame,
    Td: Union[float, int],
    ignored_requests: int,
    SP0: Union[float, int],
    SPtrim: Union[float, int],
    SPres: Union[float, int],
    SPmin: Union[float, int],
    SPmax: Union[float, int],
    SPres_max: Union[float, int],
    controller_type: str,
    variable_type: str,
    variable_subtype: str,
) -> Union[None, pd.DataFrame]:
    """Trim and respond logic verification & setpoint calculation.

    Args:
        df (dataframe): dataframe that must include timestamp (`Date/Time` column),
                        time-series data of setpoint (`setpoint` column), number of requests (`number_of_requests` column name),
                        flag_device (int or bool): flag to indicate device status (e.g., AHU). This can be integer (0: off, 1: on) or boolean (True, False),
        Td (float or int): Time delay in minutes.
        ignored_requests (int): Number of ignored requests.
        SP0 (float or int): Initial setpoint.
        SPtrim (float or int): Trim amount.
        SPres (float or int): Respond amount.
        SPmin (float or int): Minimum setpoint.
        SPmax (float or int): Maximum setpoint.
        SPres_max (float or int): Maximum response per time interval.
        controller_type (str): either `direct_acting` or `reverse_acting`. When an increase in the controller output results in an increase in the process varialbe, the `direct_acting` option should be selected. Otherwise, the `reverse_acting` option should be selected.
        variable_type (str): Type of variable to determine tolerance. Available options: temperature, airflow, waterflow, pressure. All the tolerance units are in SI (e.g., temperature: deg C, airflow: m3/s, waterflow: m3/s, pressure Pa)
        variable_subtype (str): Variable subtype to determine tolerance.
                                Available options:
                                    temperature: supply_air, zone, outdoor_air, discharge_air, return_air, general
                                    airflow: supply, outdoor_air, exhaust_air, general
                                    waterflow: hot, general
                                    pressure: static, building, general

    Return: dataframe including verification in boolean and calculated setpoint calculation results in each timestep.
    """

    # check df type
    if not isinstance(df, pd.DataFrame):
        logging.error(
            f"The type of the `df` arg must be a dataframe. It cannot be {type(df)}."
        )
        return None

    # check df index type
    if not is_datetime64_any_dtype(df.index):
        logging.error(f"Index's format is not in datetime format.")
        return None

    # check df columns
    for col in ("setpoint", "number_of_requests", "flag_device"):
        if col not in df.columns:
            logging.error(f"{col} column doesn't exist in the `df`.")
            return None

    # check the given arguments type
    if not isinstance(Td, (float, int)):
        logging.error(
            f"The type of the `Td` arg must be a float or int. It cannot be {type(Td)}."
        )
        return None

    if not isinstance(ignored_requests, int):
        logging.error(
            f"The type of the `ignored_requests` arg must be an int. It cannot be {type(ignored_requests)}."
        )
        return None

    if not isinstance(SP0, (float, int)):
        logging.error(
            f"The type of the `SP0` arg must be a float or int. It cannot be {type(SP0)}."
        )
        return None

    if not isinstance(SPtrim, (float, int)):
        logging.error(
            f"The type of the `SPtrim` arg must be a float or int. It cannot be {type(SPtrim)}."
        )
        return None

    if not isinstance(SPres, (float, int)):
        logging.error(
            f"The type of the `SPres` arg must be a float or int. It cannot be {type(SPres)}."
        )
        return None

    if not isinstance(SPmin, (float, int)):
        logging.error(
            f"The type of the `SPmin` arg must be a float or int. It cannot be {type(SPmin)}."
        )
        return None

    if not isinstance(SPmax, (float, int)):
        logging.error(
            f"The type of the `SPmax` arg must be a float or int. It cannot be {type(SPmax)}."
        )
        return None

    if not isinstance(SPres_max, (float, int)):
        logging.error(
            f"The type of the `SPres_max` arg must be a float or int. It cannot be {type(SPres_max)}."
        )
        return None

    # check if the `controller_type` is either `direct_acting` or `reverse_acting`
    if controller_type not in ("direct_acting", "reverse_acting"):
        logging.error(
            f"The `controller_type` arg must be either `direct_acting` or `reverse_acting`. It can't be `{controller_type}`."
        )
        return None

    # Check tolerance input arguments
    if variable_type not in VARIABLE_SET:
        logging.error(
            f"The `variable_type` arg must be one of temperature, airflow, waterflow, pressure. It can't be `{variable_type}`."
        )
        return None

    if variable_subtype not in VARIABLE_SUBTYPE_SET.get(variable_type):
        logging.error(
            f"The `variable_subtype` arg doesn't have a right subtype. Please check the ./constrain/tolerances.json file."
        )
        return None

    # Read the tolerance JSON file
    path_to_custom_tolerance_file = Path(__file__).parent.parent / "tolerances.json"
    with open(path_to_custom_tolerance_file) as f:
        tolerances = json.load(f)

    # Define tolerance
    tol = tolerances[variable_type]["types"][variable_subtype]

    # create "result" dataframe
    result = pd.DataFrame(
        columns=["verification", "calculated_setpoint"],
        index=df.index,
    )

    # start the T&R logic verification
    SPtrim = abs(SPtrim)
    loop_count = 0
    for current_timestamp, row in df.iterrows():
        if row["flag_device"] in (1, True) and loop_count != 0:
            # when device is on
            # Check if the device is within the last Td minute(s). If so, proceed with the trim and response logic; otherwise, skip it.
            if (
                df[
                    (df.index >= current_timestamp - pd.Timedelta(minutes=Td))
                    & (df.index <= current_timestamp)
                ]["flag_device"]
                .apply(lambda x: x in [1, True])
                .all()
            ):
                prev_timestamp_no = df.index.get_loc(current_timestamp) - 1
                prev_row_df = df.iloc[prev_timestamp_no]
                prev_row_result = result.iloc[prev_timestamp_no]

                # Extracted common variables
                num_requests = row["number_of_requests"]
                setpoint = row["setpoint"]
                prev_setpoint = prev_row_df["setpoint"]
                prev_calculated_setpoint = prev_row_result["calculated_setpoint"]

                # When the number of ignored requests is greater than or equal to the number of requests
                if num_requests <= ignored_requests:
                    if controller_type == "direct_acting":

                        # Check if the setpoint was lowered by SPtrim
                        result.loc[current_timestamp, "verification"] = (
                            True
                            if (
                                setpoint <= prev_setpoint - SPtrim + tol
                                and setpoint >= SPmin
                            )
                            else False
                        )

                        # If new_setpoint is lower than SPmin, set SPmin
                        new_setpoint = prev_calculated_setpoint - SPtrim
                        result.loc[current_timestamp, "calculated_setpoint"] = (
                            SPmin if new_setpoint < SPmin else new_setpoint
                        )

                    elif controller_type == "reverse_acting":

                        # Check if the setpoint was increased by SPtrim
                        result.loc[current_timestamp, "verification"] = (
                            True
                            if (
                                setpoint <= prev_setpoint + SPtrim - tol
                                and setpoint <= SPmax
                            )
                            else False
                        )

                        # If new_setpoint is greater than SPmax, set SPmax
                        new_setpoint = prev_calculated_setpoint + SPtrim
                        result.loc[current_timestamp, "calculated_setpoint"] = (
                            SPmax if new_setpoint >= SPmax else new_setpoint
                        )

                else:
                    # When requests > ignored requests
                    trim_amount = (num_requests - ignored_requests) * SPres
                    delta = (
                        SPres_max if abs(trim_amount) > abs(SPres_max) else trim_amount
                    )

                    if controller_type == "direct_acting":
                        # Check if setpoint was increased by correct amount
                        result.loc[current_timestamp, "verification"] = (
                            True
                            if (
                                setpoint >= prev_row_df["setpoint"] + delta - tol
                                and setpoint <= SPmax
                            )
                            else False
                        )

                        # Calculate setpoint
                        new_setpoint = prev_row_result["calculated_setpoint"] + delta
                        result.loc[current_timestamp, "calculated_setpoint"] = (
                            SPmax if new_setpoint > SPmax else new_setpoint
                        )

                    elif controller_type == "reverse_acting":
                        # Check if setpoint was increased by correct amount
                        result.loc[current_timestamp, "verification"] = (
                            True
                            if (
                                row["setpoint"] >= prev_setpoint - delta + tol
                                and row["setpoint"] >= SPmin
                            )
                            else False
                        )

                        # Calculate setpoint
                        new_setpoint = prev_calculated_setpoint - delta
                        result.loc[current_timestamp, "calculated_setpoint"] = (
                            SPmin if new_setpoint <= SPmin else new_setpoint
                        )
            else:
                # when device is on, but it hasn't been on for the Td period
                result.loc[
                    current_timestamp, ["verification", "calculated_setpoint"]
                ] = [
                    "Untested",
                    SP0,
                ]
        else:
            # when device is off
            # When the associated device is OFF, the setpoint shall be SP0
            result.loc[current_timestamp, ["verification", "calculated_setpoint"]] = [
                "Untested",
                SP0,
            ]

        loop_count += 1

    return result
