G36ReheatTerminalBoxHeatingCoilTracking
====================================================================

Brief Description
-------------------------------------------------------------------------------
Terminal box with reheat heating coil tracking discharge temperature at setpoint following the guideline 36 recommendations

Index Description
-------------------------------------------------------------------------------
   * Section 5.6.5.3 c in ASHRAE Guideline 36-2021

Datapoints Description
-------------------------------------------------------------------------------
   * operation_mode: System operation mode
   * heating_coil_command: Heating coil command
   * dat: Discharge air temperature
   * dat_spt: Discharge air temperature setpoint
   * dat_tracking_tol: Temperature tracking tolerance

Type Verification Description
-------------------------------------------------------------------------------
Procedure-based

Assertions Type
-------------------------------------------------------------------------------
Pass

Assertions Description
-------------------------------------------------------------------------------
   * only check the following if operation_mode is heating

   * if abs(dat_spt - dat) >= dat_tracking_tol (less than 1hr):

   *     pass

   * elif abs(dat_spt - dat) < dat_tracking_tol:

   *     pass

   * if dat - dat_spt >= dat_tracking_tol (continously) and heating_coil_command <= 1:

   *     pass

   * elif dat_spt - dat >= dat_tracking_tol (continuously) and vav_damper_command >= 99:

   *     pass

   * else:

   *     fail

   * end

