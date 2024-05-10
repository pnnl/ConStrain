ZoneCoolingResetDepth
====================================================================

Brief Description
-------------------------------------------------------------------------------
Cooling systems shall be equipped with controls capable of and configured to automatically restart and temporarily operate the mechanical cooling system as required to maintain zone temperatures below an adjustable cooling set point at least 5â°f above the occupied cooling set point or to prevent high space humidity levels. (case study)

Index Description
-------------------------------------------------------------------------------
   * Section 6.4.3.3.2 in 90.1-2016

Datapoints Description
-------------------------------------------------------------------------------
   * T_cool_set: Zone Thermostat Cooling Setpoint Temperature

Assertions Description
-------------------------------------------------------------------------------
   * if max(T_cool_set) - min(T_cool_set) >= 5F, then pass

Type Verification Description
-------------------------------------------------------------------------------
Procedure-based

Assertions Type
-------------------------------------------------------------------------------
Pass

