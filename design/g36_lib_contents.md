# ASHRAE Guideline 36 Verification Library

## Introduction

As our first effort to add ASHRAE Guideline 36 verification in ConStrain, a set of 17 verification items are identified and implemented based on ASHRAE Guideline 36 - 2021, multi-VAV system control sequence of operation.

The list of verification items being added are:

| Verification Item Name                                                             | Verification Class Name                                       | Verification Class Location |
| ---------------------------------------------------------------------------------- | ------------------------------------------------------------- | --------------------------- |
| Freeze Protection Stage 1                                                          | G36FreezeProtectionStage1                                     | `src/library/`              |
| Freeze Protection Stage 2                                                          | G36FreezeProtectionStage2                                     | `src/library/`              |
| Freeze Protection Stage 3                                                          | G36FreezeProtectionStage3                                     | `src/library/`              |
| Minimum Outdoor Air Control With Economizer Operation                              | G36MinOAwEconomizer                                           | `src/library/`              |
| Minimum Outdoor Air Control Without Economizer Operation                           | G36MinOAwoEconomizer                                          | `src/library/`              |
| Outdoor Air Damper Position For Systems with Relief Damper Or Fan                  | G36OutdoorAirDamperPositionForReliefDamperOrFan               | `src/library/`              |
| Outdoor Air Damper Position For Systems with Return Fan Tracking Airflow           | G36OutdoorAirDamperPositionForReturnFanAirflowTracking        | `src/library/`              |
| Outdoor Air Damper Position For Systems with Return Fan Tracking Building Pressure | G36OutdoorAirDamperPositionForReturnFanDirectBuildingPressure | `src/library/`              |
| Controller Output Command Change Rate Limit                                        | G36OutputChangeRateLimit                                      | `src/library/`              |
| Relief Air Damper Position For Systems with Return Fan Tracking Airflow            | G36ReliefAirDamperPositionForReturnFanAirflowTracking         | `src/library/`              |
| Relief Damper Status                                                               | G36ReliefDamperStatus                                         | `src/library/`              |
| Return Air Damper Position For Systems with Relief Damper Or Fan                   | G36ReturnAirDamperPositionForReliefDamperOrFan                | `src/library/`              |
| Return Air Damper Position For Systems with Return Fan Tracking Airflow            | G36ReturnAirDamperPositionForReturnFanAirflowTracking         | `src/library/`              |
| Return Air Damper Position For Systems with Return Fan Tracking Building Pressure  | G36ReturnAirDamperPositionForReturnFanDirectBuildingPressure  | `src/library/`              |
| Simultaneous Coil Heating and Coil Cooling                                         | G36SimultaneousHeatingCooling                                 | `src/library/`              |
| Supply Air Temperature Setpoint                                                    | G36SupplyAirTemperatureSetpoint                               | `src/library/`              |
| Supply fan Status                                                                  | G36SupplyFanStatus                                            | `src/library/`              |

Detailed description of Guideline 36 narrative interpretation and verification logic design are in comments of the corresponding verification item Python classes.