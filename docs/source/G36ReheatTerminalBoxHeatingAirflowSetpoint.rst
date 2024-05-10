G36ReheatTerminalBoxHeatingAirflowSetpoint
====================================================================

Brief Description
-------------------------------------------------------------------------------
Terminal box with reheat when the zone state is heating following the guideline 36 recommendations

Index Description
-------------------------------------------------------------------------------
   * Section 5.6.5.3 (a, b) in ASHRAE Guideline 36-2021

Datapoints Description
-------------------------------------------------------------------------------
   * operation_mode: System operation mode
   * zone_state: Zone state (heating, cooling, or deadband (not in either heating or cooling))
   * v_cool_max: Zone maximum cooling airflow setpoint
   * v_heat_max: Zone maximum heating airflow setpoint
   * v_heat_min: Zone minimum heating airflow setpoint
   * v_min: Occupied zone minimum airflow setpoint
   * v_spt: Active airflow setpoint
   * v_spt_tol: Airflow setpoint tolerance
   * heating_loop_output: Zone heating loop signal (from 0 to 100)
   * room_temp: Room temperature
   * space_temp_spt: Space temperature setpoint
   * ahu_sat_spt: AHU supply air temperature setpoint
   * dat: Discharge air temperature
   * dat_spt: Discharge air temperature setpoint

Type Verification Description
-------------------------------------------------------------------------------
Procedure-based

Assertions Type
-------------------------------------------------------------------------------
Pass

Assertions Description
-------------------------------------------------------------------------------
   * switch operation_mode

   *     case 'occupied'

   *         heating_maximum = max(v_heat_min, v_min)

   *         heating_minimum = max(v_heat_min, v_min)

   *     case 'cooldown'

   *         heating_maximum = v_heat_max

   *         heating_minimum = v_heat_min

   *     case 'setup', 'unoccupied'

   *         heating_maximum = 0

   *         heating_minimum = 0

   *     case 'warmup', 'setback'

   *         heating_maximum = v_heat_max

   *         heating_minimum = v_cool_max

   * 

   *     if 0 < heating_loop_output <= 50:

   *         if abs(v_spt - heating_minimum) <= tolerance and ahu_sat_spt <= dat_spt <= 11 + space_temp_spt:

   *             pass

   *         else:

   *             fail

   *     if 50 < heating_loop_output <= 100:

   *         if dat > room_temp + 3 and heating_minimum <= v_spt <= heating_maximum:

   *             pass

   *         else:

   *             untested

   *     end

