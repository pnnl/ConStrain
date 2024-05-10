G36ReturnAirDamperPositionForReturnFanDirectBuildingPressure
====================================================================

Brief Description
-------------------------------------------------------------------------------
Verify that the return air damper operation follows guideline 36 recommendations for systems with return fan with direct building pressure control

Detailed Description
-------------------------------------------------------------------------------
Verify that the return air damper operation follows the guideline 36 recommendations for supply air temperature setpoint operations

Index Description
-------------------------------------------------------------------------------
   * Section 5.16.2.3 in ASHRAE Guideline 36-2021

Datapoints Description
-------------------------------------------------------------------------------
   * heating_output: AHU heating coil output
   * cooling_output: AHU cooling coil output
   * max_ra_p: Maximum return air damper position
   * ra_p_tol: Return air damper position tolerance
   * ra_p: Return air damper position

Type Verification Description
-------------------------------------------------------------------------------
Procedure-based

Assertions Type
-------------------------------------------------------------------------------
Pass

Assertions Description
-------------------------------------------------------------------------------
   * if heating_output > 0

   *     if abs(ra_p - max_ra_p) < ra_p_tol

   *         pass

   *     else

   *         fail

   *     end

   * else if cooling_output > 0

   *     if abs(ra_p - 0) < ra_p_tol

   *         pass

   *     else

   *         fail

   *     end

   * else if abs(ra_p - (1 - rea_p) * max_ra_p) < ra_p_tol

   *     pass

   * else

   *     fail

   * end

