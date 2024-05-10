InteriorLightingControlAutomaticFullOff
====================================================================

Brief Description
-------------------------------------------------------------------------------
Interior lighting control automatic full off

Datapoints Description
-------------------------------------------------------------------------------
   * o: Number of occupants
   * total_lighting_power: Reported total lighting power (not the design total lighting power)
   * lighted_floor_area: Area lit by the device/system considered
   * tol_o: Tolerance or threshold for the number of occupants below which the system is serving an unoccupied space

Assertions Description
-------------------------------------------------------------------------------
   * The algorithm verifies that the device/system doesn't serves more than 5,000 ft2 and that if it doesn't, if occupants are not present for at least 20 minutes, the lighting power of the device/system should be less or equal to 0.02 W/ft2, otherwise, the verification fails.

Type Verification Description
-------------------------------------------------------------------------------
Procedure-based

Assertions Type
-------------------------------------------------------------------------------
Pass

