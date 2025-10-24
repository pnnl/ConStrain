import datetime
import sys
import os
import unittest

sys.path.append("./constrain")
import pandas as pd
from constrain.lib_unit_test_runner import *
from constrain.library import *


class TestCHWReset(unittest.TestCase):
    def test_chw_reset_pass_no_flow(self):
        """Test CHWReset passes when there is no chilled water flow"""
        points = [
            "temperature_air_outdoor",
            "temperature_air_outdoor_max",
            "temperature_air_outdoor_min",
            "temperature_water_chilled",
            "flow_mass_water_chilled",
            "temperature_water_chilled_setpoint_max",
            "temperature_water_chilled_setpoint_min",
        ]

        timestamp = [
            datetime(2023, 8, 1, 11, 0, 0),
            datetime(2023, 8, 1, 12, 0, 0),
            datetime(2023, 8, 1, 13, 0, 0),
            datetime(2023, 8, 1, 14, 0, 0),
            datetime(2023, 8, 1, 15, 0, 0),
        ]

        # No flow condition - should pass regardless of temperatures
        data = [
            [25, 35, 15, 8, 0.0, 12, 6],  # No flow
            [20, 35, 15, 15, 0.0, 12, 6],  # No flow
            [30, 35, 15, 5, 0.0, 12, 6],  # No flow
            [15, 35, 15, 10, 0.0, 12, 6],  # No flow
            [35, 35, 15, 7, 0.0, 12, 6],  # No flow
        ]
        df = pd.DataFrame(data, columns=points, index=timestamp)

        verification_obj = run_test_verification_with_data("CHWReset", df)
        binaryflag = verification_obj.check_bool()
        self.assertTrue(binaryflag)

    def test_chw_reset_pass_low_outdoor_temp(self):
        """Test CHWReset passes when outdoor temp is low and chilled water temp is at max setpoint"""
        points = [
            "temperature_air_outdoor",
            "temperature_air_outdoor_max",
            "temperature_air_outdoor_min",
            "temperature_water_chilled",
            "flow_mass_water_chilled",
            "temperature_water_chilled_setpoint_max",
            "temperature_water_chilled_setpoint_min",
        ]

        timestamp = [
            datetime(2023, 8, 1, 11, 0, 0),
            datetime(2023, 8, 1, 12, 0, 0),
            datetime(2023, 8, 1, 13, 0, 0),
            datetime(2023, 8, 1, 14, 0, 0),
            datetime(2023, 8, 1, 15, 0, 0),
        ]

        # Low outdoor temp (≤ min threshold), chilled water at max setpoint
        data = [
            [15, 35, 15, 12, 1.0, 12, 6],  # OAT at min, CHW at max setpoint
            [
                14,
                35,
                15,
                11.8,
                1.0,
                12,
                6,
            ],  # OAT below min, CHW near max setpoint (within tolerance)
            [13, 35, 15, 12, 1.0, 12, 6],  # OAT below min, CHW at max setpoint
            [10, 35, 15, 11.9, 1.0, 12, 6],  # OAT well below min, CHW near max setpoint
            [
                12,
                35,
                15,
                12.1,
                1.0,
                12,
                6,
            ],  # OAT below min, CHW slightly above max (should still pass)
        ]
        df = pd.DataFrame(data, columns=points, index=timestamp)

        verification_obj = run_test_verification_with_data("CHWReset", df)
        binaryflag = verification_obj.check_bool()
        self.assertTrue(binaryflag)

    def test_chw_reset_pass_high_outdoor_temp(self):
        """Test CHWReset passes when outdoor temp is high and chilled water temp is at min setpoint"""
        points = [
            "temperature_air_outdoor",
            "temperature_air_outdoor_max",
            "temperature_air_outdoor_min",
            "temperature_water_chilled",
            "flow_mass_water_chilled",
            "temperature_water_chilled_setpoint_max",
            "temperature_water_chilled_setpoint_min",
        ]

        timestamp = [
            datetime(2023, 8, 1, 11, 0, 0),
            datetime(2023, 8, 1, 12, 0, 0),
            datetime(2023, 8, 1, 13, 0, 0),
            datetime(2023, 8, 1, 14, 0, 0),
            datetime(2023, 8, 1, 15, 0, 0),
        ]

        # High outdoor temp (≥ max threshold), chilled water at min setpoint
        data = [
            [35, 35, 15, 6, 1.0, 12, 6],  # OAT at max, CHW at min setpoint
            [
                36,
                35,
                15,
                6.2,
                1.0,
                12,
                6,
            ],  # OAT above max, CHW near min setpoint (within tolerance)
            [38, 35, 15, 6, 1.0, 12, 6],  # OAT well above max, CHW at min setpoint
            [40, 35, 15, 5.8, 1.0, 12, 6],  # OAT well above max, CHW below min setpoint
            [37, 35, 15, 6.1, 1.0, 12, 6],  # OAT above max, CHW slightly above min
        ]
        df = pd.DataFrame(data, columns=points, index=timestamp)

        verification_obj = run_test_verification_with_data("CHWReset", df)
        binaryflag = verification_obj.check_bool()
        self.assertTrue(binaryflag)

    def test_chw_reset_pass_intermediate_outdoor_temp(self):
        """Test CHWReset passes when outdoor temp is intermediate and chilled water temp modulates properly"""
        points = [
            "temperature_air_outdoor",
            "temperature_air_outdoor_max",
            "temperature_air_outdoor_min",
            "temperature_water_chilled",
            "flow_mass_water_chilled",
            "temperature_water_chilled_setpoint_max",
            "temperature_water_chilled_setpoint_min",
        ]

        timestamp = [
            datetime(2023, 8, 1, 11, 0, 0),
            datetime(2023, 8, 1, 12, 0, 0),
            datetime(2023, 8, 1, 13, 0, 0),
            datetime(2023, 8, 1, 14, 0, 0),
            datetime(2023, 8, 1, 15, 0, 0),
        ]

        # Intermediate outdoor temp, chilled water temp within setpoint range
        data = [
            [25, 35, 15, 9, 1.0, 12, 6],  # OAT intermediate, CHW in middle of range
            [20, 35, 15, 10, 1.0, 12, 6],  # OAT intermediate, CHW in range
            [30, 35, 15, 7, 1.0, 12, 6],  # OAT intermediate, CHW in range
            [22, 35, 15, 11.5, 1.0, 12, 6],  # OAT intermediate, CHW near max
            [32, 35, 15, 6.5, 1.0, 12, 6],  # OAT intermediate, CHW near min
        ]
        df = pd.DataFrame(data, columns=points, index=timestamp)

        verification_obj = run_test_verification_with_data("CHWReset", df)
        binaryflag = verification_obj.check_bool()
        self.assertTrue(binaryflag)

    def test_chw_reset_fail_low_outdoor_temp_wrong_chw_temp(self):
        """Test CHWReset fails when outdoor temp is low but chilled water temp is too low"""
        points = [
            "temperature_air_outdoor",
            "temperature_air_outdoor_max",
            "temperature_air_outdoor_min",
            "temperature_water_chilled",
            "flow_mass_water_chilled",
            "temperature_water_chilled_setpoint_max",
            "temperature_water_chilled_setpoint_min",
        ]

        timestamp = [
            datetime(2023, 8, 1, 11, 0, 0),
            datetime(2023, 8, 1, 12, 0, 0),
            datetime(2023, 8, 1, 13, 0, 0),
            datetime(2023, 8, 1, 14, 0, 0),
            datetime(2023, 8, 1, 15, 0, 0),
        ]

        # Low outdoor temp but chilled water temp too low (should be at max setpoint)
        data = [
            [15, 35, 15, 8, 1.0, 12, 6],  # OAT at min, CHW too low
            [14, 35, 15, 7, 1.0, 12, 6],  # OAT below min, CHW too low
            [13, 35, 15, 9, 1.0, 12, 6],  # OAT below min, CHW too low
            [
                10,
                35,
                15,
                6,
                1.0,
                12,
                6,
            ],  # OAT well below min, CHW at min instead of max
            [12, 35, 15, 5, 1.0, 12, 6],  # OAT below min, CHW below min setpoint
        ]
        df = pd.DataFrame(data, columns=points, index=timestamp)

        verification_obj = run_test_verification_with_data("CHWReset", df)
        binaryflag = verification_obj.check_bool()
        self.assertFalse(binaryflag)

    def test_chw_reset_fail_high_outdoor_temp_wrong_chw_temp(self):
        """Test CHWReset fails when outdoor temp is high but chilled water temp is too high"""
        points = [
            "temperature_air_outdoor",
            "temperature_air_outdoor_max",
            "temperature_air_outdoor_min",
            "temperature_water_chilled",
            "flow_mass_water_chilled",
            "temperature_water_chilled_setpoint_max",
            "temperature_water_chilled_setpoint_min",
        ]

        timestamp = [
            datetime(2023, 8, 1, 11, 0, 0),
            datetime(2023, 8, 1, 12, 0, 0),
            datetime(2023, 8, 1, 13, 0, 0),
            datetime(2023, 8, 1, 14, 0, 0),
            datetime(2023, 8, 1, 15, 0, 0),
        ]

        # High outdoor temp but chilled water temp too high (should be <= max setpoint + tolerance)
        # With tolerance of 0.5, max allowed is 12.5, so values > 12.5 should fail
        data = [
            [35, 35, 15, 13, 1.0, 12, 6],  # OAT at max, CHW too high (13 > 12.5)
            [36, 35, 15, 14, 1.0, 12, 6],  # OAT above max, CHW too high (14 > 12.5)
            [
                38,
                35,
                15,
                15,
                1.0,
                12,
                6,
            ],  # OAT well above max, CHW too high (15 > 12.5)
            [
                40,
                35,
                15,
                13.5,
                1.0,
                12,
                6,
            ],  # OAT well above max, CHW too high (13.5 > 12.5)
            [37, 35, 15, 16, 1.0, 12, 6],  # OAT above max, CHW too high (16 > 12.5)
        ]
        df = pd.DataFrame(data, columns=points, index=timestamp)

        verification_obj = run_test_verification_with_data("CHWReset", df)
        binaryflag = verification_obj.check_bool()
        self.assertFalse(binaryflag)

    def test_chw_reset_fail_intermediate_outdoor_temp_wrong_chw_temp(self):
        """Test CHWReset fails when outdoor temp is intermediate but chilled water temp is outside setpoint range"""
        points = [
            "temperature_air_outdoor",
            "temperature_air_outdoor_max",
            "temperature_air_outdoor_min",
            "temperature_water_chilled",
            "flow_mass_water_chilled",
            "temperature_water_chilled_setpoint_max",
            "temperature_water_chilled_setpoint_min",
        ]

        timestamp = [
            datetime(2023, 8, 1, 11, 0, 0),
            datetime(2023, 8, 1, 12, 0, 0),
            datetime(2023, 8, 1, 13, 0, 0),
            datetime(2023, 8, 1, 14, 0, 0),
            datetime(2023, 8, 1, 15, 0, 0),
        ]

        # Intermediate outdoor temp but chilled water temp outside acceptable range
        data = [
            [25, 35, 15, 15, 1.0, 12, 6],  # OAT intermediate, CHW too high (above max)
            [20, 35, 15, 4, 1.0, 12, 6],  # OAT intermediate, CHW too low (below min)
            [30, 35, 15, 14, 1.0, 12, 6],  # OAT intermediate, CHW too high
            [22, 35, 15, 3, 1.0, 12, 6],  # OAT intermediate, CHW too low
            [32, 35, 15, 13, 1.0, 12, 6],  # OAT intermediate, CHW too high
        ]
        df = pd.DataFrame(data, columns=points, index=timestamp)

        verification_obj = run_test_verification_with_data("CHWReset", df)
        binaryflag = verification_obj.check_bool()
        self.assertFalse(binaryflag)

    def test_chw_reset_mixed_conditions(self):
        """Test CHWReset with mixed passing and failing conditions"""
        points = [
            "temperature_air_outdoor",
            "temperature_air_outdoor_max",
            "temperature_air_outdoor_min",
            "temperature_water_chilled",
            "flow_mass_water_chilled",
            "temperature_water_chilled_setpoint_max",
            "temperature_water_chilled_setpoint_min",
        ]

        timestamp = [
            datetime(2023, 8, 1, 11, 0, 0),
            datetime(2023, 8, 1, 12, 0, 0),
            datetime(2023, 8, 1, 13, 0, 0),
            datetime(2023, 8, 1, 14, 0, 0),
            datetime(2023, 8, 1, 15, 0, 0),
        ]

        # Mix of passing and failing conditions
        data = [
            [15, 35, 15, 12, 1.0, 12, 6],  # Pass: Low OAT, CHW at max
            [35, 35, 15, 14, 1.0, 12, 6],  # Fail: High OAT, CHW too high (14 > 12.5)
            [25, 35, 15, 9, 1.0, 12, 6],  # Pass: Intermediate OAT, CHW in range
            [0, 35, 15, 0, 0.0, 12, 6],  # Pass: No flow condition
            [
                20,
                35,
                15,
                15,
                1.0,
                12,
                6,
            ],  # Fail: Intermediate OAT, CHW too high (15 > 12.5)
        ]
        df = pd.DataFrame(data, columns=points, index=timestamp)

        verification_obj = run_test_verification_with_data("CHWReset", df)
        results = list(verification_obj.result)

        # Check individual results
        self.assertTrue(results[0])  # Should pass
        self.assertFalse(results[1])  # Should fail
        self.assertTrue(results[2])  # Should pass
        self.assertTrue(results[3])  # Should pass (no flow)
        self.assertFalse(results[4])  # Should fail

        # Overall should fail because not all conditions pass
        binaryflag = verification_obj.check_bool()
        self.assertFalse(binaryflag)


if __name__ == "__main__":
    unittest.main()
