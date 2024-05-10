EconomizerHighLimitA
====================================================================

Brief Description
-------------------------------------------------------------------------------
Fixed dry bulb economizer high limit

Detailed Description
-------------------------------------------------------------------------------
Economizer needs to be off when high-limit condition was satisfied. y_e_hl =f($climate zone, $toa, $tra, $hoa, $hra)

Index Description
-------------------------------------------------------------------------------
   * Table 6.5.1.1.3 in 90.1-2016

Datapoints Description
-------------------------------------------------------------------------------
   * T_oa_db: OA dry bulb temperature
   * oa_threshold: OA dry bulb threshold
   * oa_min_flow: OA minimum airflow setpoint
   * oa_flow: OA airflow

Assertions Description
-------------------------------------------------------------------------------
   * (oa_flow > oa_min_flow) AND (T_oa_db > oa_threshold)

Type Verification Description
-------------------------------------------------------------------------------
Rule-based

Assertions Type
-------------------------------------------------------------------------------
Fail

