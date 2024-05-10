G36TerminalBoxVAVDamperTracking
====================================================================

Brief Description
-------------------------------------------------------------------------------
Terminal box airflow control with vav damper following the guideline 36 recommendations

Index Description
-------------------------------------------------------------------------------
   * Section 5.5.5.4 in ASHRAE Guideline 36-2021

Datapoints Description
-------------------------------------------------------------------------------
   * vav_damper_command: Terminal box VAV damper command
   * v: Terminal box discharge airflow rate
   * v_spt: Active airflow setpoint
   * v_tracking_tol: Airflow tracking tolerance

Type Verification Description
-------------------------------------------------------------------------------
Procedure-based

Assertions Type
-------------------------------------------------------------------------------
Pass

Assertions Description
-------------------------------------------------------------------------------
   * if abs(v_spt - v) >= v_tracking_tol (less than 1hr):

   *     pass

   * elif abs(v_spt - v) < v_tracking_tol:

   *     pass

   * if v - v_spt >= v_tracking_tol (continously) and vav_damper_command <= 1:

   *     pass

   * elif v_spt - v >= v_tracking_tol (continuously) and vav_damper_command >= 99:

   *     pass

   * else:

   *     fail

   * end

