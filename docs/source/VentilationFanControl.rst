VentilationFanControl
====================================================================

Brief Description
-------------------------------------------------------------------------------
Ventilation fan control

Index Description
-------------------------------------------------------------------------------
   * Section 6.4.3.4.4 in 90.1-2016

Datapoints Description
-------------------------------------------------------------------------------
   * no_of_occ: People Occupant Count
   * Q_load: Zone Predicted Sensible Load to Setpoint Heat Transfer Rate
   * P_fan: Fan Electric Power

Assertions Description
-------------------------------------------------------------------------------
   * if Q_load = 0 and no_of_occ = 0 and P_fan != 0 then fail else pass

Type Verification Description
-------------------------------------------------------------------------------
Procedure-based

Assertions Type
-------------------------------------------------------------------------------
Pass

