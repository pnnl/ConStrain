MZSystemOccupiedStandbyVentilationZoneControl
====================================================================

Brief Description
-------------------------------------------------------------------------------
Multizone system zone standby model ventilation control

Datapoints Description
-------------------------------------------------------------------------------
   * zone_is_standby_mode: Flag indicating that the zone targeted by the verification is in occupied standby mode
   * m_oa_requested_by_system: System outdoor air setpoint
   * m_oa_zone_requirement: Outdoor air required by the targeted zone

Assertions Description
-------------------------------------------------------------------------------
   * If the targted zone is in standby mode and if the difference between the outdoor air setpoint and the last reported outdoor air setpoint when the zone was not in standby mode is greater than the outdoor air required for the zone the verification passes, it otherwise fails.

Type Verification Description
-------------------------------------------------------------------------------
Procedure-based

Assertions Type
-------------------------------------------------------------------------------
Pass

