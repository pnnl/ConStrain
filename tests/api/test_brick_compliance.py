import sys
import unittest

sys.path.append("./constrain")
from api import BrickCompliance


class TestBrickCompliance(unittest.TestCase):
    def test_constructor(self):
        # test `brick_schema_path` type
        with self.assertLogs() as logobs:
            BrickCompliance(
                brick_schema_path=["./resources/brick/Brick.ttl"],
                brick_instance_path="./resources/brick/brick_instance.ttl",
            )
            self.assertEqual(
                "ERROR:root:The `brick_schema_path` argument type must be str, but <class 'list'> type is provided.",
                logobs.output[0],
            )

        # test `brick_instance_path` type
        with self.assertLogs() as logobs:
            BrickCompliance(
                brick_schema_path="./resources/brick/Brick.ttl",
                brick_instance_path=["./resources/brick/brick_instance.ttl"],
            )
            self.assertEqual(
                "ERROR:root:The `brick_instance_path` argument type must be str, but <class 'list'> type is provided.",
                logobs.output[0],
            )

        # test `datapoint_name_conversion_path` type
        with self.assertLogs() as logobs:
            BrickCompliance(
                brick_schema_path="./resources/brick/Brick.ttl",
                brick_instance_path="./resources/brick/brick_instance.ttl",
                datapoint_name_conversion_path=[
                    "./resources/brick/query_statement.yml"
                ],
            )
            self.assertEqual(
                "ERROR:root:The `datapoint_name_conversion_path` argument type must be str, but <class 'list'> type is provided.",
                logobs.output[0],
            )

        # test `datapoint_name_conversion_path` type
        with self.assertLogs() as logobs:
            BrickCompliance(
                brick_schema_path="./resources/brick/Brick.ttl",
                brick_instance_path="./resources/brick/brick_instance.ttl",
                datapoint_name_conversion_path=[
                    "./resources/brick/verification_datapoint_info.yml"
                ],
            )
            self.assertEqual(
                "ERROR:root:The `datapoint_name_conversion_path` argument type must be str, but <class 'list'> type is provided.",
                logobs.output[0],
            )

        # test `perform_reasoning` type
        with self.assertLogs() as logobs:
            BrickCompliance(
                brick_schema_path="./resources/brick/Brick.ttl",
                brick_instance_path="./resources/brick/brick_instance.ttl",
                perform_reasoning="False",
            )
            self.assertEqual(
                "ERROR:root:The `perform_reasoning` argument type must be bool, but <class 'str'> type is provided.",
                logobs.output[0],
            )

        # test if `brick_schema_path` exists
        with self.assertLogs() as logobs:
            BrickCompliance(
                brick_schema_path="./wrong_path.ttl",
                brick_instance_path="./resources/brick/brick_instance.ttl",
            )
            self.assertEqual(
                "ERROR:root:The file doesn't exist in the provided directory. Please make sure to provide a correct `brick_schema_path`.",
                logobs.output[0],
            )

        # test if `brick_instance_path` exists
        with self.assertLogs() as logobs:
            BrickCompliance(
                brick_schema_path="./resources/brick/Brick.ttl",
                brick_instance_path="./wrong.ttl",
            )
            self.assertEqual(
                "ERROR:root:The file doesn't exist in the provided directory. Please make sure to provide a correct `brick_instance_path`.",
                logobs.output[0],
            )

        # test if `brick_instance_path` exists
        with self.assertLogs() as logobs:
            BrickCompliance(
                brick_schema_path="./resources/brick/Brick.ttl",
                brick_instance_path="./wrong_path.ttl",
            )
            self.assertEqual(
                "ERROR:root:The file doesn't exist in the provided directory. Please make sure to provide a correct `brick_instance_path`.",
                logobs.output[0],
            )

        # test if `query_statement_path` exists
        with self.assertLogs() as logobs:
            BrickCompliance(
                brick_schema_path="./resources/brick/Brick.ttl",
                brick_instance_path="./resources/brick/brick_instance.ttl",
                query_statement_path="./wrong_path.ttl",
            )
            self.assertEqual(
                "ERROR:root:The query statement file isn't found. Please verify the ./wrong_path.ttl path.",
                logobs.output[0],
            )

        # test if `datapoint_name_conversion_path` exists
        with self.assertLogs() as logobs:
            BrickCompliance(
                brick_schema_path="./resources/brick/Brick.ttl",
                brick_instance_path="./resources/brick/brick_instance.ttl",
                datapoint_name_conversion_path="./wrong_path.ttl",
            )
            self.assertEqual(
                "ERROR:root:The datapoint name conversion file isn't found. Please verify the ./wrong_path.ttl path.",
                logobs.output[0],
            )

    def test_validate_instance(self):
        # validate the instance against the brick schema
        brick_comp_obj = BrickCompliance(
            brick_schema_path="./resources/brick/Brick.ttl",
            brick_instance_path="./resources/brick/brick_instance.ttl",
        )
        is_valid, results_msg = brick_comp_obj.validate_brick_instance()

        self.assertEqual(
            is_valid,
            True,
        )

    def test_get_applicable_verification_lib_items(self):
        brick_comp_obj = BrickCompliance(
            brick_schema_path="./resources/brick/Brick.ttl",
            brick_instance_path="./resources/brick/brick_instance.ttl",
        )

        # check the `verification_lib_item_list` type
        with self.assertLogs() as logobs:
            brick_comp_obj.get_applicable_verification_lib_items({"ZoneTempControl"})
            self.assertEqual(
                "ERROR:root:The `verification_lib_item_list` argument type must be list, but <class 'set'> type is provided.",
                logobs.output[0],
            )

        # test when invalid verification lib item names are provided.
        with self.assertLogs() as logobs:
            brick_comp_obj.get_applicable_verification_lib_items(
                [
                    "wrong_name",
                    "SupplyAirTempReset",
                ]
            )
            self.assertEqual(
                "ERROR:root:The given verification library item names are invalid. Please check the names again.",
                logobs.output[0],
            )

        available_verification_item_list = (
            brick_comp_obj.get_applicable_verification_lib_items(
                [
                    "ZoneTempControl",
                    "ZoneHeatSetpointMinimum",
                    "SupplyAirTempReset",
                    "ZoneHeatingResetDepth",
                ]
            )
        )
        # `SupplyAirTempReset` isn't included b/c parameter (T_z_coo) isn't part of the query
        self.assertEqual(
            set(available_verification_item_list),
            {
                "ZoneTempControl",
                "ZoneHeatSetpointMinimum",
                "ZoneHeatingResetDepth",
            },
        )

    def test_query_verification_case_datapoints(self):
        brick_comp_obj = BrickCompliance(
            brick_schema_path="./resources/brick/Brick.ttl",
            brick_instance_path="./resources/brick/brick_instance.ttl",
        )

        # EnergyPlus variable style names
        query_result = brick_comp_obj.query_verification_case_datapoints(
            "ZoneTempControl", energyplus_naming_assembly=True
        )

        # check zone 1's datapoint names
        zone1_info = query_result[0]["datapoints_source"]["idf_output_variables"]
        self.assertEqual(
            zone1_info["T_set_cool"]["subject"],
            "zone_1",
        )
        self.assertEqual(
            zone1_info["T_set_cool"]["variable"],
            "Zone Thermostat Cooling Setpoint Temperature",
        )

        self.assertEqual(
            zone1_info["T_set_heat"]["subject"],
            "zone_1",
        )
        self.assertEqual(
            zone1_info["T_set_heat"]["variable"],
            "Zone Thermostat Heating Setpoint Temperature",
        )

        # check zone 2's datapoint names
        zone2_info = query_result[1]["datapoints_source"]["idf_output_variables"]
        self.assertEqual(
            zone2_info["T_set_cool"]["subject"],
            "zone_2",
        )
        self.assertEqual(
            zone2_info["T_set_cool"]["variable"],
            "Zone Thermostat Cooling Setpoint Temperature",
        )

        self.assertEqual(
            zone2_info["T_set_heat"]["subject"],
            "zone_2",
        )
        self.assertEqual(
            zone2_info["T_set_heat"]["variable"],
            "Zone Thermostat Heating Setpoint Temperature",
        )

        # default (non-EnergyPlus variable) style names
        query_result = brick_comp_obj.query_verification_case_datapoints(
            "ZoneTempControl", energyplus_naming_assembly=False
        )

        # check zone 1's datapoint names
        zone1_info = query_result[0]["datapoints_source"]["dev_settings"]
        self.assertEqual(
            zone1_info["T_set_cool"]["subject"],
            "zone_1",
        )
        self.assertEqual(
            zone1_info["T_set_cool"]["variable"],
            "zone_1_cooling_temperature_setpoint",
        )

        self.assertEqual(
            zone1_info["T_set_heat"]["subject"],
            "zone_1",
        )
        self.assertEqual(
            zone1_info["T_set_heat"]["variable"],
            "zone_1_heating_temperature_setpoint",
        )

        # check zone 2's datapoint names
        zone2_info = query_result[1]["datapoints_source"]["dev_settings"]
        self.assertEqual(
            zone2_info["T_set_cool"]["subject"],
            "zone_2",
        )
        self.assertEqual(
            zone2_info["T_set_cool"]["variable"],
            "zone_2_cooling_temperature_setpoint",
        )

        self.assertEqual(
            zone2_info["T_set_heat"]["subject"],
            "zone_2",
        )
        self.assertEqual(
            zone2_info["T_set_heat"]["variable"],
            "zone_2_heating_temperature_setpoint",
        )

    def test_query_with_customized_statement(self):
        brick_comp_obj = BrickCompliance(
            brick_schema_path="./resources/brick/Brick.ttl",
            brick_instance_path="./resources/brick/brick_instance.ttl",
        )

        query_statement = "SELECT ?cooling_setpoint ?heating_setpoint ?hvac_zone WHERE { ?hvac_zone a brick:HVAC_Zone . ?cooling_setpoint a brick:Zone_Air_Cooling_Temperature_Setpoint . ?heating_setpoint a brick:Zone_Air_Heating_Temperature_Setpoint . ?hvac_zone brick:hasPoint ?cooling_setpoint, ?heating_setpoint . }"

        # wrong `custom_query_statement` type
        with self.assertLogs() as logobs:
            brick_comp_obj.query_with_customized_statement(
                list(query_statement),
                "ZoneTempControl",
            )
            self.assertEqual(
                "ERROR:root:The `custom_query_statement` argument type must be str, but <class 'list'> type is provided.",
                logobs.output[0],
            )

        # wrong `verification_item_lib_name` type
        with self.assertLogs() as logobs:
            brick_comp_obj.query_with_customized_statement(
                query_statement,
                ["ZoneTempControl"],
            )
            self.assertEqual(
                "ERROR:root:The `verification_item_lib_name` argument type must be str, but <class 'list'> type is provided.",
                logobs.output[0],
            )

        # wrong `energyplus_naming_assembly` type
        with self.assertLogs() as logobs:
            brick_comp_obj.query_with_customized_statement(
                query_statement, "ZoneTempControl", energyplus_naming_assembly="True"
            )
            self.assertEqual(
                "ERROR:root:The `energyplus_naming_assembly` argument type must be bool, but <class 'str'> type is provided.",
                logobs.output[0],
            )

        # test the quality check
        # the `modified_query_statement` intentionally omits the `?heating_setpoint`
        modified_query_statement = "SELECT ?cooling_setpoint ?hvac_zone WHERE { ?hvac_zone a brick:HVAC_Zone . ?cooling_setpoint a brick:Zone_Air_Cooling_Temperature_Setpoint . ?heating_setpoint a brick:Zone_Air_Heating_Temperature_Setpoint . ?hvac_zone brick:hasPoint ?cooling_setpoint, ?heating_setpoint . }"
        with self.assertLogs() as logobs:
            brick_comp_obj.query_with_customized_statement(
                modified_query_statement,
                "ZoneTempControl",
            )
            self.assertEqual(
                "WARNING:root:The number of datapoints with the customized query statement is 1 excluding the `hvac_zone` and the number of required datapoints for ZoneTempControl verification item is 2. The two numbers must be the same.",
                logobs.output[0],
            )


if __name__ == "__main__":
    unittest.main()
