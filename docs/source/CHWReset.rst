CHWReset
====================================================================

Brief Description
-------------------------------------------------------------------------------
Chilled water supply water temperature reset

Detailed Description
-------------------------------------------------------------------------------
Chilled-water systems with a design capacity exceeding 300,000 btu/h supplying chilled water to comfort conditioning systems shall include controls that automatically reset supply water temperatures by representative building loads (including return water temperature) or by outdoor air temperature. where ddc is used to control valves, the set point shall be reset based on valve positions until one valve is nearly wide open or setpoint limits of the system equipment or application have been reached. (case study)

Index Description
-------------------------------------------------------------------------------
   * Section 6.5.4.4 in 90.1-2016

Datapoints Description
-------------------------------------------------------------------------------
   * T_oa_db: OA dry-bulb temperature
   * T_oa_max: OA dry-bulb upper threshold
   * T_oa_min: OA dry-bulb lower threshold
   * T_chw: Chilled water temp observed from the system node
   * m_chw: Chilled water flow rate
   * T_chw_max_set: Chilled water maximum temp setpoint
   * T_chw_min_set: Chilled water minimum temp setpoint

Assertions Description
-------------------------------------------------------------------------------
   * When m_chw > 0, T_chw <= T_chw_max_set and T_chw >= T_chw_min_set; When m_chw <= 0 , always pass

Type Verification Description
-------------------------------------------------------------------------------
Rule-based

Assertions Type
-------------------------------------------------------------------------------
Pass

