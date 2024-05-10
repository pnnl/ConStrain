ExteriorLightingControlDaylightOff
====================================================================

Brief Description
-------------------------------------------------------------------------------
Exterior lighting control occupancy sensing reduction

Datapoints Description
-------------------------------------------------------------------------------
   * is_sun_up: Flag that indicates if the sun has risen
   * daylight_sensed: Amount of daylight sensed by a sensor, this should be expressed in the same unit as the setpoint
   * daylight_setpoint: Daylight setpoint, or thresholds, used to determine if the exterior lighting system should be turned off
   * total_lighting_power: Reported total lighting power (not the design total lighting power)

Assertions Description
-------------------------------------------------------------------------------
   * The algorithm verifies that the exterior lighting is off when the sun has risen, or when there is a sufficient amount of daylight. If the exterior lighting system is not off during these situation, the verification fails, otherwise it passes.

Type Verification Description
-------------------------------------------------------------------------------
Procedure-based

Assertions Type
-------------------------------------------------------------------------------
Pass

