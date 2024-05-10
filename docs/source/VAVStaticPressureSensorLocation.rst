VAVStaticPressureSensorLocation
====================================================================

Brief Description
-------------------------------------------------------------------------------
Vav static pressure sensor location requirement

Index Description
-------------------------------------------------------------------------------
   * Section 6.5.3.2.2 in 90.1-2016

Datapoints Description
-------------------------------------------------------------------------------
   * p_fan_set: Static pressure setpoint
   * tol_P_fan: Tolerance for VAV box static pressure sensor

Assertions Description
-------------------------------------------------------------------------------
   * if static pressure setpoint is no greater than 1.2 in of water (298.608 Pa) then pass else fail

Type Verification Description
-------------------------------------------------------------------------------
Procedure-based

Assertions Type
-------------------------------------------------------------------------------
Pass

