import unittest, sys, os, datetime, copy, pandas

sys.path.append("./constrain")

from api import DataAdapter


class TestDataAdapter(unittest.TestCase):
    def test_digest_long_csv(self):
        test_file_path = "./tests/api/data/long_sample.csv"
        new_df = DataAdapter.digest_long_csv(
            data_path=test_file_path,
            time_col="Timestamp",
            point_name_assembly=["System", "Building", "Equipment", "Variable"],
            value_col="Value",
        )
        new_df.to_csv("./tests/api/data/wide_sample_output.csv")
        assert len(new_df) == 7
        assert os.path.isfile("./tests/api/data/wide_sample_output.csv")


if __name__ == "__main__":
    unittest.main()
