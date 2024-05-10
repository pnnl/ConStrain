G36OutdoorAirDamperPositionForReliefDamperOrFan
====================================================================

Brief Description
-------------------------------------------------------------------------------
Verify that the outdoor air damper operation follows guideline 36 recommendations for systems with relief damper/fan

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
   * economizer_high_limit_reached: Economizer high limit flag
   * oa_p: Outdoor air damper position
   * min_oa_p: Minimum outdoor air damper position
   * max_oa_p: Maximum outdoor air damper position
   * oa_p_tol: Outdoor air damper position tolerance
   * ra_p_tol: Return air damper position tolerance
   * ra_p: Return air damper position
   * max_ra_p: Maximum return air damper position

Type Verification Description
-------------------------------------------------------------------------------
Procedure-based

Assertions Type
-------------------------------------------------------------------------------
Pass

Assertions Description
-------------------------------------------------------------------------------
   * if heating_output > 0

   *     if abs(oa_p - min_oa_p) < oa_p_tol

   *         pass

   *     else

   *         fail

   *     end

   * else if cooling_output > 0

   *     if economizer_high_limit_reached

   *         if abs(oa_p - min_oa_p) < oa_p_tol

   *             pass

   *         else

   *             fail

   *         end

   *     else

   *         if abs(oa_p - max_oa_p) < oa_p_tol

   *             pass

   *         else

   *             fail

   *         end

   *     end

   * else if ra_p < max_ra_p

   *     if abs(oa_p - max_oa_p) < oa_p_tol

   *         pass

   *     else

   *         fail

   *     end

   * else if abs(ra_p - max_ra_p) < ra_p_tol

   *     if min_oa_p < oa_p < max_oa_p

   *         pass

   *     else

   *         fail

   *     end

   * end

