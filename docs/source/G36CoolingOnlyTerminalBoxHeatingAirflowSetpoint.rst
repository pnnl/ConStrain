G36CoolingOnlyTerminalBoxHeatingAirflowSetpoint
====================================================================

Brief Description
-------------------------------------------------------------------------------
Cooling only terminal box airflow control when the zone state is heating following the guideline 36 recommendations

Index Description
-------------------------------------------------------------------------------
   * Section 5.5.5.3 in ASHRAE Guideline 36-2021

Datapoints Description
-------------------------------------------------------------------------------
   * operation_mode: System operation mode
   * zone_state: Zone state (heating, cooling, or deadband (not in either heating or cooling))
   * v_cool_max: Zone maximum cooling airflow setpoint
   * v_heat_max: Zone maximum heating airflow setpoint
   * v_min: Occupied zone minimum airflow setpoint
   * v_spt: Active airflow setpoint

Type Verification Description
-------------------------------------------------------------------------------
Procedure-based

Assertions Type
-------------------------------------------------------------------------------
Pass

Assertions Description
-------------------------------------------------------------------------------
   * switch operation_mode

   * case 'occupied'

   *     heating_maximum = v_heat_max

   *     minimum = v_min

   * case 'cooldown', 'setup', 'unoccupied'

   *     heating_maximum = 0

   *     minimum = 0

   * case 'warmup', 'setback'

   *     heating_maximum = v_cool_max

   *     minimum = 0

   * 

   * if minimum <= v_spt <= heating_maximum

   *     pass

   * else

   *     fail

   * end

