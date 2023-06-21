import logging
from typing import Union

import pandas as pd


def TrimRespondLogic(
    df: pd.DataFrame,
    Td: Union[float, int],
    ignored_requests: int,
    SPtrim: Union[float, int],
    SPres: Union[float, int],
    SPmin: Union[float, int],
    SPmax: Union[float, int],
    SPres_max: Union[float, int],
    tol: Union[float, int],
    controller_type: str,
) -> pd.DataFrame:
    """Trim and respond logic verification logic.

    Args:
        df (dataframe): dataframe that must include timestamp (`Date/Time` column), time-series data of setpoint (`setpoint` column), number of requests (`number_of_requests` column name),
        Td (float or int): Time delay in minutes.
        ignored_requests (int): Number of ignored requests.
        SPtrim (float or int): Minimum setpoint.
        SPres (float or int): Maximum setpoint.
        SPmin (float or int):
        SPmax (float or int): Maximum response per time interval.
        SPres_max (float or int):
        tol (float or int): tolerance.
        controller_type (str): either `direct_acting` or `reverse_acting` depending on whether output increases/decreases as the measurement increases/decreases.

    Return: dataframe including verification result in each timestep.
    """

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
    if controller_type not in ["direct_acting", "reverse_acting"]:
        logging.error(
            f"`controller_type` arg must be either `direct_acting` or `reverse_acting`. It can't be `{controller_type}`."
        )
        return None

    # create "result" dataframe
    result = pd.DataFrame(columns=["result"], index=df["Date/Time"])
    result.drop(result.index[0], inplace=True)

    # start the T&R logic verification
    actual_start_time = df.at[0, "Date/Time"] + pd.Timedelta(minutes=Td)
    for idx, row in df.iterrows():
        current_time = row["Date/Time"]
        if idx > 0 and current_time >= actual_start_time:
            prev_row = df.loc[idx - 1]
            # when the number of ignored requests is greater than or equal to the number of requests
            if row["number_of_requests"] <= ignored_requests:
                if controller_type == "direct_acting":
                    if (
                        row["setpoint"] <= prev_row["setpoint"] - SPtrim + tol
                        and row["setpoint"] >= SPmin
                    ):
                        result.loc[current_time, "result"] = True
                    else:
                        result.loc[current_time, "result"] = False

                elif controller_type == "reverse_acting":
                    if (
                        row["setpoint"] <= prev_row["setpoint"] + SPtrim - tol
                        and row["setpoint"] <= SPmax
                    ):
                        result.loc[current_time, "result"] = True
                    else:
                        result.loc[current_time, "result"] = False

            else:
                trim_amount = (row["number_of_requests"] - ignored_requests) * SPres
                if abs(trim_amount) > abs(SPres_max):
                    delta = SPres_max
                else:
                    delta = trim_amount

                if controller_type == "direct_acting":
                    if (
                        row["setpoint"] >= prev_row["setpoint"] + delta - tol
                        and row["setpoint"] <= SPmax
                    ):
                        result.loc[current_time, "result"] = True
                    else:
                        result.loc[current_time, "result"] = False

                elif controller_type == "reverse_acting":
                    if (
                        row["setpoint"] >= prev_row["setpoint"] - delta + tol
                        and row["setpoint"] >= SPmin
                    ):
                        result.loc[current_time, "result"] = True
                    else:
                        result.loc[current_time, "result"] = False

    return result
