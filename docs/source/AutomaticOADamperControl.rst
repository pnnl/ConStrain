AutomaticOADamperControl
====================================================================

Brief Description
-------------------------------------------------------------------------------
Hvac system shall be turned on and off everyday

Index Description
-------------------------------------------------------------------------------
   * Section 6.4.3.4.2 in 90.1-2016

Datapoints Description
-------------------------------------------------------------------------------
   * o: Number of occupants
   * m_oa: Air terminal outdoor air volume flow rate
   * eco_onoff: Air system outdoor air economizer status
   * tol_o: Tolerance for the number of occupants
   * tol_m_oa: Tolerance for the air terminal air volume flow rate

Assertions Description
-------------------------------------------------------------------------------
   * if no_of_occ <= 0 + tol and m_ea + m_oa > 0 and eco_onoff = 0, then false else pass

Type Verification Description
-------------------------------------------------------------------------------
Procedure-based

Assertions Type
-------------------------------------------------------------------------------
Pass

