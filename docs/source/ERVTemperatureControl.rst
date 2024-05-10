ERVTemperatureControl
====================================================================

Brief Description
-------------------------------------------------------------------------------
Tspr tool software development

Index Description
-------------------------------------------------------------------------------
   * None

Datapoints Description
-------------------------------------------------------------------------------
   * MIN_OA_FLOW: Minimum outdoor air flow rate
   * OA_FLOW: Outdoor air flow rate
   * NOM_FLOW: Heat exchanger's norminal flow rate
   * HX_DSN_EFF_HTG: Heat exchanger heating effectiveness at the nominal air flow rate
   * HX_DSN_EFF_HTG_75_PCT: Heat exchanger heating effectiveness at 75% of the nominal air flow rate
   * HX_DSN_EFF_CLG: Heat exchanger cooling effectiveness at the nominal air flow rate
   * HX_DSN_EFF_CLG_75_PCT: Heat exchanger cooling effectiveness at 75% of the nominal air flow rate
   * T_OA: Outdoor air dry-bulb temperature
   * T_SO: Supply air temperature
   * T_SO_SP: Supply air temperature setpoint
   * T_EI: Zone air temperature

Assertions Description
-------------------------------------------------------------------------------
   * Check that the ERV is bypassed during economizer operation; During non-economizer operation, if the outdoor air flow rate, 1) if T_SO > T_SO_SP the ERV is not operating correctly if T_OA < T_EI and the ERV is running, T_OA > T_EI and the ERV is NOT running and the operating sensible efficiency of the ERV is NOT close to the operating design value, 2) if T_SO < T_SO_SP the ERV is NOT running and the operating sensible efficiency of the ERV is NOT close to the operating design value

Type Verification Description
-------------------------------------------------------------------------------
Procedure-based

Assertions Type
-------------------------------------------------------------------------------
Pass

