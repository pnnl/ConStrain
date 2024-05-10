G36ReliefAirDamperPositionForReturnFanAirflowTracking
====================================================================

Brief Description
-------------------------------------------------------------------------------
Verify that the outdoor air damper operation follows guideline 36 recommendations for systems with return fan with airflow tracking

Detailed Description
-------------------------------------------------------------------------------
Verify that the outdoor air damper operation follows the guideline 36 recommendations for supply air temperature setpoint operations

Index Description
-------------------------------------------------------------------------------
   * Section 5.16.2.3 in ASHRAE Guideline 36-2021

Datapoints Description
-------------------------------------------------------------------------------
   * heating_output: AHU heating coil output
   * cooling_output: AHU cooling coil output
   * max_rea_p: Maximum return air damper position
   * rea_p_tol: Return air damper position tolerance
   * rea_p: Return air damper position
   * ra_p: Relief air damper position

Type Verification Description
-------------------------------------------------------------------------------
Procedure-based

Assertions Type
-------------------------------------------------------------------------------
Pass

Assertions Description
-------------------------------------------------------------------------------
   * if heating_output > 0

   *     if abs(rea_p - 0) < rea_p_tol

   *         pass

   *     else

   *         fail

   *     end

   * else if cooling_output > 0

   *     if abs(rea_p - max_rea_p) < rea_p_tol

   *         pass

   *     else

   *         fail

   *     end

   * else if abs(rea_p - (1 - ra_p) * max_rea_p) < rea_p_tol

   *     pass

   * else

   *     fail

   * end

