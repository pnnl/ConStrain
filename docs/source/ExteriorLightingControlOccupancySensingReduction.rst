ExteriorLightingControlOccupancySensingReduction
====================================================================

Brief Description
-------------------------------------------------------------------------------
Exterior lighting control occupancy sensing reduction

Datapoints Description
-------------------------------------------------------------------------------
   * o: Number of occupants
   * total_lighting_power: Reported total lighting power (not the design total lighting power)
   * tol_o: Tolerance or threshold for the number of occupants below which the system is serving an unoccupied space

Assertions Description
-------------------------------------------------------------------------------
   * The algorithm verifies that the exterior lighting is controlled based on occupancy. It fails if the maximum reported total lighting power is greater than 1500 W and if the total mnaximum lighting power is not reduced by half when occupancy has not been detected for 15 mins. Otherwise, it passes.

Type Verification Description
-------------------------------------------------------------------------------
Procedure-based

Assertions Type
-------------------------------------------------------------------------------
Pass

