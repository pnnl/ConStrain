ZoneHeatingResetDepth
====================================================================

Brief Description
-------------------------------------------------------------------------------
Heating systems shall be equipped with controls capable of and configured to automatically restart and temporarily operate the system as required to maintain zone temperatures above an adjustable heating set point at least 10â°f below (will be 60â°f) the occupied heating set point. (case study)

Index Description
-------------------------------------------------------------------------------
   * Section 6.4.3.3.2 in 90.1-2016

Datapoints Description
-------------------------------------------------------------------------------
   * T_heat_set: Zone Thermostat Heating Setpoint Temperature

Assertions Description
-------------------------------------------------------------------------------
   * if max(T_heat_set) - min(T_heat_set) >= 10F, then pass

Type Verification Description
-------------------------------------------------------------------------------
Procedure-based

Assertions Type
-------------------------------------------------------------------------------
Pass

