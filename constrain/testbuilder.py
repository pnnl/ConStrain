"""Module takes in item and data frame, and return test codes"""

from constrain.item import Item
import pandas as pd


class Testbuilder:
    """Build and run assertions for simulation i/o verification against ASHRAE items"""

    def __init__(self, df: pd.DataFrame, item: Item):
        """

        Args:
            df: pandas dataframe containing points timeseries needed for the item
            item: `Item` object
        """
        self.df = df.copy(deep=True)
        self.item = item
        self.assertions = item.assertions

    def run_all(self):
        """run timeseries against all assertions of the item

        Returns:
            dict of running results. key is assertion string, value is the list of boolean results

        """
        results = {}
        for assertion in self.assertions:
            self.df[assertion] = None
            results[assertion] = self.assert_code(assertion)
        return results

    def assert_code(self, assertion: str):
        """helper

        Args:
            assertion: e.g.  "$OA_timestep > $OA_min_sys and $Cool_sys_out > 0"

        Returns:
            list of assertion results for the dataframe, only for one assertion at a time.
        """
        code = assertion
        for col in self.df.columns:
            code = code.replace(f"${col}", f"row['{col}']")

        result_list = []
        for index, row in self.df.iterrows():
            warmhole = locals()
            exec(f"flag = ({code})", globals(), warmhole)
            result_list.append(warmhole["flag"])
        self.df[assertion] = result_list

        return result_list
