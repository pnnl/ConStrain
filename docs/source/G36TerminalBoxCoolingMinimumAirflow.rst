G36TerminalBoxCoolingMinimumAirflow
====================================================================

Brief Description
-------------------------------------------------------------------------------
Terminal box in cooling mode needs maintain minimum airflow when supply air temperature is high following the guideline 36 recommendations

Index Description
-------------------------------------------------------------------------------
   * Section 5.5.5.1.a in Guideline 36-2021

   * Section 5.6.5.1.a in Guideline 36-2021

Datapoints Description
-------------------------------------------------------------------------------
   * operation_mode: System operation mode
   * zone_state: Zone state (heating, cooling, or deadband (not in either heating or cooling))
   * v_min: Occupied zone minimum airflow setpoint
   * ahu_sat_spt: AHU supply air temperature setpoint
   * v_spt: Active airflow setpoint
   * v_spt_tol: Airflow setpoint tolerance
   * room_temp: Room temperature

Type Verification Description
-------------------------------------------------------------------------------
Procedure-based

Assertions Type
-------------------------------------------------------------------------------
Pass

Assertions Description
-------------------------------------------------------------------------------
   * if ahu_sat_spt <= room_temp:

   *     untested

   * else:

   *     switch operation_mode

   *         case 'occupied'

   *             minimum = v_min

   *         case 'cooldown', 'setup', 'warmup', 'setback', 'unoccupied'

   *             minimum = 0

   *     if v_spt - v_spt_tol > minimum:

   *         fail

   *     else:

   *         pass

