HeatRejectionFanVariableFlowControl
====================================================================

Brief Description
-------------------------------------------------------------------------------
The cooling tower fan power is 30% of the design value at 50% flow

Index Description
-------------------------------------------------------------------------------
   * Section 6.5.5.2.1 in 90.1-2016

Datapoints Description
-------------------------------------------------------------------------------
   * ct_P_fan: Cooling Tower Fan Power
   * ct_P_fan_dsgn: Cooling Tower Design Fan Power
   * ct_m_fan_ratio: Cooling Tower Air Flow Rate Ratio
   * ct_m_fan_dsgn: Cooling Tower Design Air Flow

Assertions Description
-------------------------------------------------------------------------------
   * Verify that at 5% flow, the cooling tower fan power is 30% of the design value. Since simulation results might not include that exact point, we use a regression based approach to determining if the code requirement is met

Type Verification Description
-------------------------------------------------------------------------------
Rule-based

Assertions Type
-------------------------------------------------------------------------------
Pass

