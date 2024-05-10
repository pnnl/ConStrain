ZoneHeatSetpointMinimum
====================================================================

Brief Description
-------------------------------------------------------------------------------
Zone heating setpoint reset temperature minimum value check

Detailed Description
-------------------------------------------------------------------------------
Heating systems located in climate zones 2-8 shall be equipped with controls that have the capability to automatically restart and temporarily operate the system as required to maintain zone temperatures above a heating setpoint adjustable down to 55â°f or lower. (case study)

Index Description
-------------------------------------------------------------------------------
   * Section 6.4.3.2.2 in 90.1-2004

Datapoints Description
-------------------------------------------------------------------------------
   * T_heat_set: Zone Thermostat Heating Setpoint Temperature

Assertions Description
-------------------------------------------------------------------------------
   * if min(T_heat_set) <= 55Â°F, then pass

Type Verification Description
-------------------------------------------------------------------------------
Procedure-based

Assertions Type
-------------------------------------------------------------------------------
Pass

