EconomizerHighLimitB
====================================================================

Brief Description
-------------------------------------------------------------------------------
Differential dry bulb economizer high limit

Detailed Description
-------------------------------------------------------------------------------
Check the 90.1-2016 table

Index Description
-------------------------------------------------------------------------------
   * Table 6.5.1.1.3 in 90.1-2016

Datapoints Description
-------------------------------------------------------------------------------
   * T_oa_db: OA dry bulb temperature
   * ret_a_temp: Retuan air temperature
   * oa_min_flow: OA minimum airflow setpoint
   * oa_flow: OA airflow

Assertions Description
-------------------------------------------------------------------------------
   * (oa_flow > oa_min_flow) AND (ret_a_temp < T_oa_db)

Type Verification Description
-------------------------------------------------------------------------------
Rule-based

Assertions Type
-------------------------------------------------------------------------------
Fail

