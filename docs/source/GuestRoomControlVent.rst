GuestRoomControlVent
====================================================================

Brief Description
-------------------------------------------------------------------------------
Verify whether there is guest room outdoor airflow control during operation hours

Index Description
-------------------------------------------------------------------------------
   * Section 6.4.3.3.5.2 in 90.1-2016

Datapoints Description
-------------------------------------------------------------------------------
   * damper_sch: Damper Schdule
   * m_oa_fraction: Air System Outdoor Air Flow Fraction
   * O_sch: Occupant schedule
   * m_oa_heat_design: Design Heating Air Flow Rate
   * m_oa_cool_design: Design Cooling Air Flow Rate
   * volume: Zone Volume
   * v_outdoor_per_zone: Outdoor Air Flow per Zone Floor Area
   * tol_occ: Tolerence for occupant Schedule
   * tol_oa_flow: Tolerance for Outdoor Airflow

Assertions Description
-------------------------------------------------------------------------------
   * Check the two different airflow control logics when the room is/isn't rented out

Type Verification Description
-------------------------------------------------------------------------------
Rule-based

Assertions Type
-------------------------------------------------------------------------------
Pass

