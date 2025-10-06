import datetime
import sys
import os
import unittest

sys.path.append("./constrain")
import pandas as pd
from constrain.lib_unit_test_runner import *
from constrain.library import *


class TestHWReset(unittest.TestCase):
    def test_hw_reset_pass_no_flow(self):
        """Test HWReset passes when there is no hot water flow"""
        points = [
            "temperature_air_outdoor",
            "temperature_air_outdoor_max",
            "temperature_air_outdoor_min",
            "temperature_water_hot",
            "flow_mass_water_hot",
            "temperature_water_hot_setpoint_max",
            "temperature_water_hot_setpoint_min",
        ]

        timestamp = [
            datetime(2023, 1, 15, 11, 0, 0),
            datetime(2023, 1, 15, 12, 0, 0),
            datetime(2023, 1, 15, 13, 0, 0),
            datetime(2023, 1, 15, 14, 0, 0),
            datetime(2023, 1, 15, 15, 0, 0),
        ]

        # No flow condition - should pass regardless of temperatures
        data = [
            [-5, 15, -10, 45, 0.0, 80, 40],  # No flow
            [5, 15, -10, 30, 0.0, 80, 40],  # No flow
            [10, 15, -10, 70, 0.0, 80, 40],  # No flow
            [-10, 15, -10, 50, 0.0, 80, 40],  # No flow
            [15, 15, -10, 35, 0.0, 80, 40],  # No flow
        ]
        df = pd.DataFrame(data, columns=points, index=timestamp)

        verification_obj = run_test_verification_with_data("HWReset", df)
        binaryflag = verification_obj.check_bool()
        self.assertTrue(binaryflag)

    def test_hw_reset_pass_low_outdoor_temp(self):
        """Test HWReset passes when outdoor temp is low and hot water temp is at max setpoint"""
        points = [
            "temperature_air_outdoor",
            "temperature_air_outdoor_max",
            "temperature_air_outdoor_min",
            "temperature_water_hot",
            "flow_mass_water_hot",
            "temperature_water_hot_setpoint_max",
            "temperature_water_hot_setpoint_min",
        ]

        timestamp = [
            datetime(2023, 1, 15, 11, 0, 0),
            datetime(2023, 1, 15, 12, 0, 0),
            datetime(2023, 1, 15, 13, 0, 0),
            datetime(2023, 1, 15, 14, 0, 0),
            datetime(2023, 1, 15, 15, 0, 0),
        ]

        # Low outdoor temp (≤ min threshold), hot water at max setpoint
        data = [
            [-10, 15, -10, 80, 1.0, 80, 40],  # OAT at min, HW at max setpoint
            [
                -12,
                15,
                -10,
                79.5,
                1.0,
                80,
                40,
            ],  # OAT below min, HW near max setpoint (within tolerance)
            [-15, 15, -10, 80, 1.0, 80, 40],  # OAT below min, HW at max setpoint
            [
                -20,
                15,
                -10,
                79.8,
                1.0,
                80,
                40,
            ],  # OAT well below min, HW near max setpoint
            [
                -8,
                15,
                -10,
                80.2,
                1.0,
                80,
                40,
            ],  # OAT below min, HW slightly above max (should still pass)
        ]
        df = pd.DataFrame(data, columns=points, index=timestamp)

        verification_obj = run_test_verification_with_data("HWReset", df)
        binaryflag = verification_obj.check_bool()
        self.assertTrue(binaryflag)

    def test_hw_reset_pass_high_outdoor_temp(self):
        """Test HWReset passes when outdoor temp is high and hot water temp is at min setpoint"""
        points = [
            "temperature_air_outdoor",
            "temperature_air_outdoor_max",
            "temperature_air_outdoor_min",
            "temperature_water_hot",
            "flow_mass_water_hot",
            "temperature_water_hot_setpoint_max",
            "temperature_water_hot_setpoint_min",
        ]

        timestamp = [
            datetime(2023, 1, 15, 11, 0, 0),
            datetime(2023, 1, 15, 12, 0, 0),
            datetime(2023, 1, 15, 13, 0, 0),
            datetime(2023, 1, 15, 14, 0, 0),
            datetime(2023, 1, 15, 15, 0, 0),
        ]

        # High outdoor temp (≥ max threshold), hot water at min setpoint
        data = [
            [15, 15, -10, 40, 1.0, 80, 40],  # OAT at max, HW at min setpoint
            [
                16,
                15,
                -10,
                40.3,
                1.0,
                80,
                40,
            ],  # OAT above max, HW near min setpoint (within tolerance)
            [20, 15, -10, 40, 1.0, 80, 40],  # OAT well above max, HW at min setpoint
            [
                25,
                15,
                -10,
                39.5,
                1.0,
                80,
                40,
            ],  # OAT well above max, HW below min setpoint
            [18, 15, -10, 40.2, 1.0, 80, 40],  # OAT above max, HW slightly above min
        ]
        df = pd.DataFrame(data, columns=points, index=timestamp)

        verification_obj = run_test_verification_with_data("HWReset", df)
        binaryflag = verification_obj.check_bool()
        self.assertTrue(binaryflag)

    def test_hw_reset_pass_intermediate_outdoor_temp(self):
        """Test HWReset passes when outdoor temp is intermediate and hot water temp modulates properly"""
        points = [
            "temperature_air_outdoor",
            "temperature_air_outdoor_max",
            "temperature_air_outdoor_min",
            "temperature_water_hot",
            "flow_mass_water_hot",
            "temperature_water_hot_setpoint_max",
            "temperature_water_hot_setpoint_min",
        ]

        timestamp = [
            datetime(2023, 1, 15, 11, 0, 0),
            datetime(2023, 1, 15, 12, 0, 0),
            datetime(2023, 1, 15, 13, 0, 0),
            datetime(2023, 1, 15, 14, 0, 0),
            datetime(2023, 1, 15, 15, 0, 0),
        ]

        # Intermediate outdoor temp, hot water temp within setpoint range
        data = [
            [0, 15, -10, 60, 1.0, 80, 40],  # OAT intermediate, HW in middle of range
            [-5, 15, -10, 70, 1.0, 80, 40],  # OAT intermediate, HW in range
            [10, 15, -10, 50, 1.0, 80, 40],  # OAT intermediate, HW in range
            [-2, 15, -10, 75, 1.0, 80, 40],  # OAT intermediate, HW near max
            [12, 15, -10, 45, 1.0, 80, 40],  # OAT intermediate, HW near min
        ]
        df = pd.DataFrame(data, columns=points, index=timestamp)

        verification_obj = run_test_verification_with_data("HWReset", df)
        binaryflag = verification_obj.check_bool()
        self.assertTrue(binaryflag)

    def test_hw_reset_fail_low_outdoor_temp_wrong_hw_temp(self):
        """Test HWReset fails when outdoor temp is low but hot water temp is too low"""
        points = [
            "temperature_air_outdoor",
            "temperature_air_outdoor_max",
            "temperature_air_outdoor_min",
            "temperature_water_hot",
            "flow_mass_water_hot",
            "temperature_water_hot_setpoint_max",
            "temperature_water_hot_setpoint_min",
        ]

        timestamp = [
            datetime(2023, 1, 15, 11, 0, 0),
            datetime(2023, 1, 15, 12, 0, 0),
            datetime(2023, 1, 15, 13, 0, 0),
            datetime(2023, 1, 15, 14, 0, 0),
            datetime(2023, 1, 15, 15, 0, 0),
        ]

        # Low outdoor temp but hot water temp too low (should be at max setpoint)
        data = [
            [-10, 15, -10, 60, 1.0, 80, 40],  # OAT at min, HW too low
            [-12, 15, -10, 50, 1.0, 80, 40],  # OAT below min, HW too low
            [-15, 15, -10, 65, 1.0, 80, 40],  # OAT below min, HW too low
            [
                -20,
                15,
                -10,
                40,
                1.0,
                80,
                40,
            ],  # OAT well below min, HW at min instead of max
            [-8, 15, -10, 35, 1.0, 80, 40],  # OAT below min, HW below min setpoint
        ]
        df = pd.DataFrame(data, columns=points, index=timestamp)

        verification_obj = run_test_verification_with_data("HWReset", df)
        binaryflag = verification_obj.check_bool()
        self.assertFalse(binaryflag)

    def test_hw_reset_fail_high_outdoor_temp_wrong_hw_temp(self):
        """Test HWReset fails when outdoor temp is high but hot water temp is too high"""
        points = [
            "temperature_air_outdoor",
            "temperature_air_outdoor_max",
            "temperature_air_outdoor_min",
            "temperature_water_hot",
            "flow_mass_water_hot",
            "temperature_water_hot_setpoint_max",
            "temperature_water_hot_setpoint_min",
        ]

        timestamp = [
            datetime(2023, 1, 15, 11, 0, 0),
            datetime(2023, 1, 15, 12, 0, 0),
            datetime(2023, 1, 15, 13, 0, 0),
            datetime(2023, 1, 15, 14, 0, 0),
            datetime(2023, 1, 15, 15, 0, 0),
        ]

        # High outdoor temp but hot water temp too high (should be at min setpoint)
        data = [
            [15, 15, -10, 60, 1.0, 80, 40],  # OAT at max, HW too high
            [16, 15, -10, 80, 1.0, 80, 40],  # OAT above max, HW at max instead of min
            [20, 15, -10, 55, 1.0, 80, 40],  # OAT well above max, HW too high
            [25, 15, -10, 70, 1.0, 80, 40],  # OAT well above max, HW too high
            [18, 15, -10, 50, 1.0, 80, 40],  # OAT above max, HW too high
        ]
        df = pd.DataFrame(data, columns=points, index=timestamp)

        verification_obj = run_test_verification_with_data("HWReset", df)
        binaryflag = verification_obj.check_bool()
        self.assertFalse(binaryflag)

    def test_hw_reset_fail_intermediate_outdoor_temp_wrong_hw_temp(self):
        """Test HWReset fails when outdoor temp is intermediate but hot water temp is outside setpoint range"""
        points = [
            "temperature_air_outdoor",
            "temperature_air_outdoor_max",
            "temperature_air_outdoor_min",
            "temperature_water_hot",
            "flow_mass_water_hot",
            "temperature_water_hot_setpoint_max",
            "temperature_water_hot_setpoint_min",
        ]

        timestamp = [
            datetime(2023, 1, 15, 11, 0, 0),
            datetime(2023, 1, 15, 12, 0, 0),
            datetime(2023, 1, 15, 13, 0, 0),
            datetime(2023, 1, 15, 14, 0, 0),
            datetime(2023, 1, 15, 15, 0, 0),
        ]

        # Intermediate outdoor temp but hot water temp outside acceptable range
        data = [
            [0, 15, -10, 90, 1.0, 80, 40],  # OAT intermediate, HW too high (above max)
            [-5, 15, -10, 30, 1.0, 80, 40],  # OAT intermediate, HW too low (below min)
            [10, 15, -10, 85, 1.0, 80, 40],  # OAT intermediate, HW too high
            [-2, 15, -10, 25, 1.0, 80, 40],  # OAT intermediate, HW too low
            [12, 15, -10, 95, 1.0, 80, 40],  # OAT intermediate, HW too high
        ]
        df = pd.DataFrame(data, columns=points, index=timestamp)

        verification_obj = run_test_verification_with_data("HWReset", df)
        binaryflag = verification_obj.check_bool()
        self.assertFalse(binaryflag)

    def test_hw_reset_mixed_conditions(self):
        """Test HWReset with mixed passing and failing conditions"""
        points = [
            "temperature_air_outdoor",
            "temperature_air_outdoor_max",
            "temperature_air_outdoor_min",
            "temperature_water_hot",
            "flow_mass_water_hot",
            "temperature_water_hot_setpoint_max",
            "temperature_water_hot_setpoint_min",
        ]

        timestamp = [
            datetime(2023, 1, 15, 11, 0, 0),
            datetime(2023, 1, 15, 12, 0, 0),
            datetime(2023, 1, 15, 13, 0, 0),
            datetime(2023, 1, 15, 14, 0, 0),
            datetime(2023, 1, 15, 15, 0, 0),
        ]

        # Mix of passing and failing conditions
        data = [
            [-10, 15, -10, 80, 1.0, 80, 40],  # Pass: Low OAT, HW at max
            [
                20,
                15,
                -10,
                45,
                1.0,
                80,
                40,
            ],  # Fail: High OAT (well above max), HW too high
            [0, 15, -10, 55, 1.0, 80, 40],  # Pass: Intermediate OAT, HW in range
            [5, 15, -10, 0, 0.0, 80, 40],  # Pass: No flow condition
            [
                -5,
                15,
                -10,
                85,
                1.0,
                80,
                40,
            ],  # Fail: Intermediate OAT, HW too high (above max 80.5)
        ]
        df = pd.DataFrame(data, columns=points, index=timestamp)

        verification_obj = run_test_verification_with_data("HWReset", df)
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

    def test_hw_reset_edge_case_boundary_conditions(self):
        """Test HWReset with boundary conditions at exact thresholds"""
        points = [
            "temperature_air_outdoor",
            "temperature_air_outdoor_max",
            "temperature_air_outdoor_min",
            "temperature_water_hot",
            "flow_mass_water_hot",
            "temperature_water_hot_setpoint_max",
            "temperature_water_hot_setpoint_min",
        ]

        timestamp = [
            datetime(2023, 1, 15, 11, 0, 0),
            datetime(2023, 1, 15, 12, 0, 0),
            datetime(2023, 1, 15, 13, 0, 0),
            datetime(2023, 1, 15, 14, 0, 0),
            datetime(2023, 1, 15, 15, 0, 0),
        ]

        # Test exact boundary conditions with tolerance considerations
        data = [
            [
                -10.5,
                15,
                -10,
                79.5,
                1.0,
                80,
                40,
            ],  # OAT at min threshold (with tolerance), HW near max
            [
                15.5,
                15,
                -10,
                40.5,
                1.0,
                80,
                40,
            ],  # OAT at max threshold (with tolerance), HW near min
            [
                -9.5,
                15,
                -10,
                79.5,
                1.0,
                80,
                40,
            ],  # OAT just above min threshold, HW acceptable
            [
                14.5,
                15,
                -10,
                40.5,
                1.0,
                80,
                40,
            ],  # OAT just below max threshold, HW acceptable
            [
                2.5,
                15,
                -10,
                60,
                1.0,
                80,
                40,
            ],  # OAT exactly in middle, HW in middle of range
        ]
        df = pd.DataFrame(data, columns=points, index=timestamp)

        verification_obj = run_test_verification_with_data("HWReset", df)
        binaryflag = verification_obj.check_bool()
        self.assertTrue(binaryflag)


if __name__ == "__main__":
    unittest.main()
