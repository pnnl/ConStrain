ZoneCoolingSetpointMaximum
====================================================================

Brief Description
-------------------------------------------------------------------------------
 cooling systems located in climate zones 1b, 2b, and 3b shall be equipped with controls that have the capability to automatically restart and temporarily operate the system as required to maintain zone temperatures below a cooling setpoint adjustable up to 90â°f or higher or to prevent high space humidity levels. (case study)

Index Description
-------------------------------------------------------------------------------
   * Section 6.4.3.2.2 in 90.1-2004

Datapoints Description
-------------------------------------------------------------------------------
   * T_cool_set: Zone Thermostat Cooling Setpoint Temperature

Assertions Description
-------------------------------------------------------------------------------
   * if max(T_cool_set) >= 90F, then pass

Type Verification Description
-------------------------------------------------------------------------------
Procedure-based

Assertions Type
-------------------------------------------------------------------------------
Pass

