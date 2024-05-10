NightCycleOperation
====================================================================

Brief Description
-------------------------------------------------------------------------------
Tspr tool software development

Index Description
-------------------------------------------------------------------------------
   * None

Datapoints Description
-------------------------------------------------------------------------------
   * T_zone: Zone Air Temperature
   * HVAC_operation_sch: HVAC Operation Schedule
   * T_heat_set: Zone Thermostat Heating Setpoint Temperature
   * T_cool_set: Zone Thermostat Cooling Setpoint Temperature
   * Fan_elec_rate: Fan Electricity Rate

Assertions Description
-------------------------------------------------------------------------------
   * if T_heat_set <= T_zone <= T_cool_set and Fan_elec_rate ==0 then x1=0 else x1=1, if (T_zone > T_cool_set and Fan_elec_rate >= 0) and (T_zone < T_heat_set and Fan_elec_rate>0) then x2=0 else x=1, if x1 and x2=0, then pass, elseif x1=0 and x2=1 then fail, elseif x1=1 and x2=0 then fail, elseif x1=1 and x2=1 then fail

Type Verification Description
-------------------------------------------------------------------------------
Procedure-based

Assertions Type
-------------------------------------------------------------------------------
Pass

