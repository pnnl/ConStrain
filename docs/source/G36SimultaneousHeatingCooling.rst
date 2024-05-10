G36SimultaneousHeatingCooling
====================================================================

Brief Description
-------------------------------------------------------------------------------
Verifiy that both the heating and cooling coil are not operating at the same time

Index Description
-------------------------------------------------------------------------------
   * Section 5.16.2.3 in ASHRAE Guideline 36-2021

Datapoints Description
-------------------------------------------------------------------------------
   * heating_output: AHU heating coil output
   * cooling_output: AHU cooling coil output

Type Verification Description
-------------------------------------------------------------------------------
Procedure-based

Assertions Type
-------------------------------------------------------------------------------
Pass

Assertions Description
-------------------------------------------------------------------------------
   * if heating_output > 0 and cooling_output > 0

   *     fail

   * else

   *     pass

   * end

