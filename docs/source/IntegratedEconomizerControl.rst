IntegratedEconomizerControl
====================================================================

Brief Description
-------------------------------------------------------------------------------
Economizer shall be integrated with mechanical cooling

Detailed Description
-------------------------------------------------------------------------------
Economizer systems shall be integrated with the mechanical cooling system and be capable of and configured to provide partial cooling even when additional mechanical cooling is required to meet the remainder of the cooling load. controls shall not false load the mechanical cooling systems by limiting or disabling the economizer or by any other means, such as hot-gas bypass, except at the lowest stage of mechanical cooling. (case study, add non-integrated economizer (check each seprate on, but not both on)

Index Description
-------------------------------------------------------------------------------
   * Section 6.5.1.3 in 90.1-2016

Datapoints Description
-------------------------------------------------------------------------------
   * oa_min_flow: OA minimum airflow setpoint
   * oa_flow: OA airflow
   * ccoil_out: Cooling coil transfer

Assertions Description
-------------------------------------------------------------------------------
   * ((oa_flow > oa_min_flow) AND (ccoil_out > 0)) never happens

Type Verification Description
-------------------------------------------------------------------------------
Procedure-based

Assertions Type
-------------------------------------------------------------------------------
Fail

