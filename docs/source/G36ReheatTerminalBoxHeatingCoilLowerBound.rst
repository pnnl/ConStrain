G36ReheatTerminalBoxHeatingCoilLowerBound
====================================================================

Brief Description
-------------------------------------------------------------------------------
Terminal box with reheat heating coil needs to keep discharge air temp no lower than 10c when occupied following the guideline 36 recommendations

Index Description
-------------------------------------------------------------------------------
   * Section 5.6.5.4 in Guideline 36-2021

Datapoints Description
-------------------------------------------------------------------------------
   * operation_mode: System operation mode
   * heating_coil_command: Heating coil command
   * dat: Discharge air temperature

Type Verification Description
-------------------------------------------------------------------------------
Procedure-based

Assertions Type
-------------------------------------------------------------------------------
Pass

Assertions Description
-------------------------------------------------------------------------------
   * if operation_mode != 'occupied':

   *     untested

   * if operation_mode == 'occupied':

   *     if dat < 10 and heating_coil_command < 99:

   *         fail

   *     else:

   *         pass

   * end

