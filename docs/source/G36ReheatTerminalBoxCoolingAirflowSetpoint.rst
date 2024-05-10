G36ReheatTerminalBoxCoolingAirflowSetpoint
====================================================================

Brief Description
-------------------------------------------------------------------------------
Terminal box with reheat when the zone state is cooling following the guideline 36 recommendations

Index Description
-------------------------------------------------------------------------------
   * Section 5.6.5.1 in ASHRAE Guideline 36-2021

Datapoints Description
-------------------------------------------------------------------------------
   * operation_mode: System operation mode
   * zone_state: Zone state (heating, cooling, or deadband (not in either heating or cooling))
   * v_cool_max: Maximum cooling airflow setpoint
   * v_min: Occupied zone minimum airflow setpoint
   * v_spt: Active airflow setpoint
   * heating_coil_command: Heating coil command
   * heating_coil_command_tol: Heating coil command saturation tolerance
   * dat: Discharge air temperature
   * dat_min_spt: Minimum discharge air temperature setpoint

Type Verification Description
-------------------------------------------------------------------------------
Procedure-based

Assertions Type
-------------------------------------------------------------------------------
Pass

Assertions Description
-------------------------------------------------------------------------------
   * if dat > dat_min_spt and heating_coil_command > heating_coil_command_tol

   *     fail

   * else

   *    switch operation_mode

   *    case 'occupied'

   *        cooling_maximum = v_cool_max

   *        minimum = v_min

   *    case 'cooldown', 'setup'

   *        cooling_maximum = v_cool_max

   *        minimum = 0

   *    case 'warmup', 'setback', 'unoccupied'

   *        cooling_maximum = 0

   *        minimum = 0

   *    

   *    if cooling_minimum <= v_spt <= cooling_maximum

   *        pass

   *    else

   *        fail

   * end

