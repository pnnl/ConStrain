import unittest, sys, os, datetime, copy, pandas

# Add the project root to the path so we can import constrain
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from constrain.api import DataAdapter


class TestDataAdapter(unittest.TestCase):
    def test_digest_long_csv(self):
        test_file_path = "./tests/api/data/long_sample.csv"
        new_df = DataAdapter.digest_long_csv(
            data_path=test_file_path,
            time_col="Timestamp",
            point_name_assembly=["System", "Building", "Equipment", "Sensor"],
            value_col="Value",
        )
        new_df.to_csv("./tests/api/data/wide_sample_output.csv")
        assert len(new_df) == 7
        assert os.path.isfile("./tests/api/data/wide_sample_output.csv")
        os.remove("./tests/api/data/wide_sample_output.csv")


if __name__ == "__main__":
    unittest.main()
