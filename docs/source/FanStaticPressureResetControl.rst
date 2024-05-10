FanStaticPressureResetControl
====================================================================

Brief Description
-------------------------------------------------------------------------------
The set point is reset lower until one zone damper is nearly wide open

Index Description
-------------------------------------------------------------------------------
   * Section 6.5.3.2.3 in 90.1-2016

Datapoints Description
-------------------------------------------------------------------------------
   * p_set: Static pressure setpoint
   * d_VAV_x: VAV Damper x Position (includes all VAV dampers served by the system under test
   * tol: Tolerance for VAV box damper position openings
   * p_set_min: : Minimum static pressure setpoint threshold

Assertions Description
-------------------------------------------------------------------------------
   * if d_VAV(n) (n=1,2,...,N) < 0.9 and p_set(t) > p_set(t-1), then fail else pass

Type Verification Description
-------------------------------------------------------------------------------
Procedure-based

Assertions Type
-------------------------------------------------------------------------------
Pass

