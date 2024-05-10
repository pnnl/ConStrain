G36CoolingOnlyTerminalBoxDeadbandAirflowSetpoint
====================================================================

Brief Description
-------------------------------------------------------------------------------
Cooling only terminal box airflow control when the zone state is deadband following the guideline 36 recommendations

Index Description
-------------------------------------------------------------------------------
   * Section 5.5.5.2 in ASHRAE Guideline 36-2021

Datapoints Description
-------------------------------------------------------------------------------
   * operation_mode: System operation mode
   * zone_state: Zone state (heating, cooling, or deadband (not in either heating or cooling))
   * v_min: Occupied zone minimum airflow setpoint
   * v_spt: Active airflow setpoint
   * v_spt_tol: Airflow setpoint tolerance

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

   *     minimum = v_min

   * case 'cooldown', 'setup', 'warmup', 'setback', 'unoccupied'

   *     minimum = 0

   * 

   * if abs(v_spt - minimum) <= v_spt_tol

   *     pass

   * else

   *     fail

   * end

