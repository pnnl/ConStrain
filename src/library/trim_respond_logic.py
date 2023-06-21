import pandas as pd
import logging, sys
from typing import Union


def TrimRespondLogic(
    df: pd.DataFrame,
    setpoint_name: str,
    Td: Union[float, int],
    I: int,
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
        df (dataframe): dataframe including time-series data of setpoint, number of requests,
        setpoint_name (str): Name of the setpoint in the `df` argument.
        Td (float or int): Time delay in minutes.
        I (int): Number of ignored requests.
        SPtrim (float or int): Minimum setpoint.
        SPres (float or int): Maximum setpoint.
        SPmin (float or int):
        SPmax (float or int): Maximum response per time interval.
        SPres_max (float or int):
        tol (float or int): tolerance.
        controller_type (str): either `direct_acting` or `reverse_acting` depending on whether output increases/decreases as the measurement increases/decreases.

    Return: a dataframe including verification result in each timestep.
    """
    # check the given arguments type
    if not isinstance(I, int):
        logging.error(
            f"The type of the `I` arg must be an int. It cannot be {type(I)}."
        )
        return None
    if not (isinstance(SPtrim, float) or isinstance(SPtrim, int)):
        logging.error(
            f"The type of the `SPtrim` arg must be a float. It cannot be {type(SPtrim)}."
        )
        return None
    if not (isinstance(SPres, float) or isinstance(SPres, int)):
        logging.error(
            f"The type of the `SPres` arg must be a float. It cannot be {type(SPres)}."
        )
        return None

    if not (isinstance(SPmin, float) or isinstance(SPmin, int)):
        logging.error(
            f"The type of the `SPmin` arg must be a float. It cannot be {type(SPmin)}."
        )
        return None
    if not (isinstance(SPmax, float) or isinstance(SPmax, int)):
        logging.error(
            f"The type of the `SPmax` arg must be a float. It cannot be {type(SPmax)}."
        )
        return None

    if not (isinstance(SPres_max, float) or isinstance(SPres_max, int)):
        logging.error(
            f"The type of the `SPres_max` arg must be a float. It cannot be {type(SPres_max)}."
        )
        return None

    if not (isinstance(tol, float) and isinstance(tol, int)):
        logging.error(
            f"The type of the `tol` arg must be a float. It cannot be {type(tol)}."
        )
        return None

    # create "result" column
    result = pd.DataFrame(columns=["result"])

    # start the T&R logic verification
    for idx, row in df.iterrows():
        if idx > 0 and row["Date/Time"] >= df.at[0, "Date/Time"] + pd.Timedelta(
            minutes=Td
        ):
            prev_row = df.loc[idx - 1]
            # when the number of ignored requests is greater than or equal to the number of requests
            if row["number_of_requests"] <= I:
                if controller_type == "direct_acting":
                    if (
                        row[setpoint_name] <= prev_row[setpoint_name] - SPtrim + tol
                        and row[setpoint_name] >= SPmin
                    ):
                        result.loc[idx, "result"] = True
                    else:
                        result.loc[idx, "result"] = False

                elif controller_type == "reverse_acting":
                    if (
                        row[setpoint_name] <= prev_row[setpoint_name] + SPtrim - tol
                        and row[setpoint_name] <= SPmax
                    ):
                        result.loc[idx, "result"] = True
                    else:
                        result.loc[idx, "result"] = False

            else:
                trim_amount = (row["number_of_requests"] - I) * SPres
                if abs(trim_amount) > abs(SPres_max):
                    delta = SPres_max
                else:
                    delta = trim_amount

                if controller_type == "direct_acting":
                    if (
                        row[setpoint_name] >= prev_row[setpoint_name] + delta - tol
                        and row[setpoint_name] <= SPmax
                    ):
                        result.loc[idx, "result"] = True
                    else:
                        result.loc[idx, "result"] = False

                elif controller_type == "reverse_acting":
                    if (
                        row[setpoint_name] >= prev_row[setpoint_name] - delta + tol
                        and row[setpoint_name] >= SPmin
                    ):
                        result.loc[idx, "result"] = True
                    else:
                        result.loc[idx, "result"] = False

    return result
