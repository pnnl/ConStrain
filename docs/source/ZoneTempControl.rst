ZoneTempControl
====================================================================

Brief Description
-------------------------------------------------------------------------------
Zone temperature setpoint deadband >= 5f (2.77c)

Detailed Description
-------------------------------------------------------------------------------
Where used to control both heating and cooling, zone thermostatic controls shall be capable of and configured to provide a temperature range or dead band of at least 5â°f within which the supply of heating and cooling energy to the zone is shut off or reduced to a minimum. (case study for zone temperature reset, not for this one)

Index Description
-------------------------------------------------------------------------------
   * Section 6.4.3.1.2 in 90.1-2016

Datapoints Description
-------------------------------------------------------------------------------
   * T_set_cool: Zone cooling temperature setpoint
   * T_set_heat: Zone heating temperature setpoint

Assertions Description
-------------------------------------------------------------------------------
   * T_set_cool - T_set_heat > 5F (2.77C)

Type Verification Description
-------------------------------------------------------------------------------
Rule-based

Assertions Type
-------------------------------------------------------------------------------
Pass

