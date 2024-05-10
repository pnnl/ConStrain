ERVRatio
====================================================================

Brief Description
-------------------------------------------------------------------------------
Erv ratio of at least 50%

Detailed Description
-------------------------------------------------------------------------------
Energy recovery systems required by this section shall result in an enthalpy recovery ratio of at least 50%. a 50% enthalpy recovery ratio shall mean a change in the enthalpy of the outdoor air supply equal to 50% of the difference between the outdoor air and entering exhaust air enthalpies at design conditions.

Index Description
-------------------------------------------------------------------------------
   * Section 6.5.6.1 in 90.1-2016

Datapoints Description
-------------------------------------------------------------------------------
   * oa_enth: OA enthalpy
   * ret_enth: Return air enthalpy
   * oa_enth_ERV: OA enthalpy after ERV

Assertions Description
-------------------------------------------------------------------------------
   * (oa_enth_ERV - oa_enth)/(ret_enth - oa_enth) > = 50%  happens at least once in winter design day

Type Verification Description
-------------------------------------------------------------------------------
Procedure-based

Assertions Type
-------------------------------------------------------------------------------
Pass

