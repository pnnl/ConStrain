DemandControlVentilation
====================================================================

Brief Description
-------------------------------------------------------------------------------
Demand control ventilation verification for high-occupancy areas

Index Description
-------------------------------------------------------------------------------
   * Section 6.4.3.8 in 90.1-2016

Datapoints Description
-------------------------------------------------------------------------------
   * v_oa: Zone Air Terminal Outdoor Air Volume Flow Rate
   * s_ahu: status of HVAC system operation
   * s_eco: Air System Outdoor Air Economizer Status
   * no_of_occ: People Occupant Count

Assertions Description
-------------------------------------------------------------------------------
   * i) If v_oa is constant over time, NO DCV presents. ii) If v_oa has two clusters, DCV with hbinary control presents. iii) v_oa is linearly correlated to o_ahu, DCV with occupant-counting based control presents

Type Verification Description
-------------------------------------------------------------------------------
Rule-based

Assertions Type
-------------------------------------------------------------------------------
Pass

