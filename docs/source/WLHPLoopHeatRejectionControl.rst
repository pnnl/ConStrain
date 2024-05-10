WLHPLoopHeatRejectionControl
====================================================================

Brief Description
-------------------------------------------------------------------------------
Water-loop heat pump heat rejection control

Index Description
-------------------------------------------------------------------------------
   * Section 6.5.2.2.3 (a) in 90.1-2016

Datapoints Description
-------------------------------------------------------------------------------
   * T_max_heating_loop: maximum temperature of heating loop
   * T_min_cooling_loop: minimum temperature of cooling loop
   * m_pump: Pump Mass Flow Rate
   * tol: Tolerance for water-loop temperature difference

Assertions Description
-------------------------------------------------------------------------------
   * If the temperature difference between the maximum heating loop and minimum heating loop when the pump runs is greater than 11.11 °C, then pass else fail

Type Verification Description
-------------------------------------------------------------------------------
Procedure-based

Assertions Type
-------------------------------------------------------------------------------
Pass

