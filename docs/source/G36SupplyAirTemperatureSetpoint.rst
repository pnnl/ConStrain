G36SupplyAirTemperatureSetpoint
====================================================================

Brief Description
-------------------------------------------------------------------------------
Supply air temperature operation following the guideline 36 recommendations

Detailed Description
-------------------------------------------------------------------------------
Verify that the supply air temperature setpoint of a system follows the guideline 36 recommendations

Index Description
-------------------------------------------------------------------------------
   * Section 5.16.2.2 in ASHRAE Guideline 36-2021

Datapoints Description
-------------------------------------------------------------------------------
   * operation_mode: System operation mode
   * oa_t: Outdoor air temperature
   * t_max: Maximum supply air temperature setpoint based on requests
   * sa_t_sp_ac: Actual supply air temperature setpoint
   * oa_t_min: Minimum outdoor air temperature for linear SAT reset
   * oa_t_max: Maximum outdoor air temperature for linear SAT reset
   * min_clg_sa_t_sp: Minimum cooling supply air temperature setpoint
   * max_clg_sa_t_sp: Maximum cooling supply air temperature setpoint
   * sa_sp_tol: supply air temperature tolerance

Type Verification Description
-------------------------------------------------------------------------------
Procedure-based

Assertions Type
-------------------------------------------------------------------------------
Pass

Assertions Description
-------------------------------------------------------------------------------
   * if t_max > max_clg_sa_t_sp

   *     fail

   * end

   * 

   * switch operation_mode

   * case 'cooldown'

   *     sa_t_sp = min_clg_sa_t_sp

   * case 'warmup', 'setback

   *     sa_t_sp = 35 # 95 F

   * case 'occupied', 'setup'

   *     if oa_t <= oa_t_min

   *         sa_t_sp = t_max

   *     else if oa_t >= oa_t_max

   *         sa_t_sp = min_clg_sa_t_sp

   *     else

   *         sa_t_sp = (oa_t - oa_t_min) * (t_max - min_clg_sa_t_sp) / (oa_t_min - oa_t_max) + t_max 

   * # linear interpolation

   *     end

   * end

   * 

   * if abs(sa_t_sp - sa_t_s_ac) < sa_sp_tol

   *     pass

   * else

   *     fail

   * end

