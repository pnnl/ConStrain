G36OutdoorAirDamperPositionForReturnFanDirectBuildingPressure
====================================================================

Brief Description
-------------------------------------------------------------------------------
Verify that the outdoor air damper operation follows guideline 36 recommendations for systems with return fan with direct building pressure control

Detailed Description
-------------------------------------------------------------------------------
Verify that the outdoor air damper operation follows the guideline 36 recommendations for supply air temperature setpoint operations

Index Description
-------------------------------------------------------------------------------
   * Section 5.16.2.3 in ASHRAE Guideline 36-2021

Datapoints Description
-------------------------------------------------------------------------------
   * oa_p: Outdoor air damper position
   * max_oa_p: Maximum outdoor air damper position
   * oa_p_tol: Outdoor air damper position tolerance

Type Verification Description
-------------------------------------------------------------------------------
Procedure-based

Assertions Type
-------------------------------------------------------------------------------
Pass

Assertions Description
-------------------------------------------------------------------------------
   * if abs(oa_p - max_oa_p) < oa_p_tol

   *     pass

   * else

   *     fail

   * end

