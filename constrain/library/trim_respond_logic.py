import logging
from typing import Union

import pandas as pd
from pandas.api.types import is_datetime64_any_dtype


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
    tol: Union[float, int],
    controller_type: str,
) -> Union[None, pd.DataFrame]:
    """Trim and respond logic verification & setpoint calculation.

    Args:
        df (dataframe): dataframe that must include timestamp (`Date/Time` column), time-series data of setpoint (`setpoint` column), number of requests (`number_of_requests` column name),
        Td (float or int): Time delay in minutes.
        ignored_requests (int): Number of ignored requests.
        SP0 (float or int): Initial setpoint.
        SPtrim (float or int): Trim amount.
        SPres (float or int): Respond amount.
        SPmin (float or int): Minimum setpoint.
        SPmax (float or int): Maximum setpoint.
        SPres_max (float or int): Maximum response per time interval.
        tol (float or int): tolerance.
        controller_type (str): either `direct_acting` or `reverse_acting`. When an increase in the controller output results in an increase in the process barialbe, the `direct_acting` option should be selected. Otherwise, the `reverse_acting` option should be selected.

    Return: dataframe including verification in boolean and setpoint calculation results in each timestep.
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
    for col in ("setpoint", "number_of_requests"):
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
            f"The type of the `SP0` arg must be a float or int. It cannot be {type(tol)}."
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

    if not isinstance(tol, (float, int)):
        logging.error(
            f"The type of the `tol` arg must be a float or int. It cannot be {type(tol)}."
        )
        return None

    # check if the `controller_type` is either `direct_acting` or `reverse_acting`
    if controller_type not in ("direct_acting", "reverse_acting"):
        logging.error(
            f"`controller_type` arg must be either `direct_acting` or `reverse_acting`. It can't be `{controller_type}`."
        )
        return None

    # calculate actual start time
    initial_timestamp = df.index[0]
    actual_start_time = initial_timestamp + pd.Timedelta(minutes=Td)

    # create "result" dataframe
    result = pd.DataFrame(
        columns=["verification", "setpoint"],
        index=df[df.index >= actual_start_time].index,
    )

    # preprocess df, cut off before Td
    copied_df = df.copy()[df.index > actual_start_time]

    # setup an initial value
    result.loc[actual_start_time, "verification"] = True
    if initial_timestamp == actual_start_time:
        result.loc[actual_start_time, "setpoint"] = SP0
    else:
        try:
            df.loc[actual_start_time, "setpoint"]
        except KeyError:
            logging.error(
                f"The delayed timestamp must be included in the `df` timestamp."
            )
            return None

    # start the T&R logic verification
    for current_timestamp, row in copied_df.iterrows():
        prev_row_df = copied_df.iloc[copied_df.index.get_loc(current_timestamp) - 1]
        prev_row_result = result.iloc[result.index.get_loc(current_timestamp) - 1]

        # when the number of ignored requests is greater than or equal to the number of requests
        if row["number_of_requests"] <= ignored_requests:
            if controller_type == "direct_acting":
                # determine T&R logic was implemented correctly (verification)
                if (
                    row["setpoint"] <= prev_row_df["setpoint"] + SPtrim + tol
                    and row["setpoint"] >= SPmin
                ):
                    result.loc[current_timestamp, "verification"] = True
                else:
                    result.loc[current_timestamp, "verification"] = False

                # calculate setpoint by T&R logic
                new_setpoint = prev_row_result["setpoint"] + SPtrim
                result.loc[current_timestamp, "setpoint"] = (
                    SPmin if new_setpoint < SPmin else new_setpoint
                )

            elif controller_type == "reverse_acting":
                # determine T&R logic was implemented correctly (verification)
                if (
                    row["setpoint"] <= prev_row_df["setpoint"] - SPtrim - tol
                    and row["setpoint"] <= SPmax
                ):
                    result.loc[current_timestamp, "verification"] = True
                else:
                    result.loc[current_timestamp, "verification"] = False

                # calculate setpoint by T&R logic
                new_setpoint = prev_row_result["setpoint"] - SPtrim
                result.loc[current_timestamp, "setpoint"] = (
                    SPmax if new_setpoint >= SPmax else new_setpoint
                )

        else:
            trim_amount = (row["number_of_requests"] - ignored_requests) * SPres
            if abs(trim_amount) > abs(SPres_max):
                delta = SPres_max
            else:
                delta = trim_amount

            if controller_type == "direct_acting":
                # determine T&R logic was implemented correctly (verification)
                if (
                    row["setpoint"] >= prev_row_df["setpoint"] + delta - tol
                    and row["setpoint"] <= SPmax
                ):
                    result.loc[current_timestamp, "verification"] = True
                else:
                    result.loc[current_timestamp, "verification"] = False

                # calculate setpoint by T&R logic
                new_setpoint = prev_row_result["setpoint"] + delta
                result.loc[current_timestamp, "setpoint"] = (
                    SPmax if new_setpoint > SPmax else new_setpoint
                )

            elif controller_type == "reverse_acting":
                # determine T&R logic was implemented correctly (verification)
                if (
                    row["setpoint"] >= prev_row_df["setpoint"] - delta + tol
                    and row["setpoint"] >= SPmin
                ):
                    result.loc[current_timestamp, "verification"] = True
                else:
                    result.loc[current_timestamp, "verification"] = False

                # calculate setpoint by T&R logic
                new_setpoint = prev_row_result["setpoint"] - delta
                result.loc[current_timestamp, "setpoint"] = (
                    SPmin if new_setpoint <= SPmin else new_setpoint
                )

    return result
