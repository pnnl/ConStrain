EconomizerHighLimitD
====================================================================

Brief Description
-------------------------------------------------------------------------------
Differential enthalpy + fixed dry bulb economizer high limit (case study)

Detailed Description
-------------------------------------------------------------------------------
N/a

Index Description
-------------------------------------------------------------------------------
   * Table 6.5.1.1.3 in 90.1-2016

Datapoints Description
-------------------------------------------------------------------------------
   * T_oa_db: OA dry bulb temperature
   * oa_threshold: OA dry bulb threshold
   * oa_min_flow: OA minimum airflow setpoint
   * oa_flow: OA airflow
   * oa_enth: OA enthalpy
   * ret_a_enth: Return air enthalpy

Assertions Description
-------------------------------------------------------------------------------
   * oa_flow > oa_min_flow) AND ((ret_a_enth < oa_enth) OR (T_oa_db > oa_threshold))

Type Verification Description
-------------------------------------------------------------------------------
Rule-based

Assertions Type
-------------------------------------------------------------------------------
Fail

