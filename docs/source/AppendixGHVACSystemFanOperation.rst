AppendixGHVACSystemFanOperation
====================================================================

Brief Description
-------------------------------------------------------------------------------
Verify hvac system fan operation as per ashrae 90.1 appendix g rules

Datapoints Description
-------------------------------------------------------------------------------
   * o: Number of occupants
   * fan_runtime_fraction: Fan runtime fraction (fraction of time the fan ran for the reported period)
   * m_oa: System outdoor air flow rate
   * tol_o: Tolerance or threshold for the number of occupants below which the system is serving an unoccupied space

Assertions Description
-------------------------------------------------------------------------------
   * If the system never provides outdoor air the verification is untested. The verification fails if the system fan is not continuously running during an occupied period, it passes if it does. The verification fails if the system is always operating continuously during occupied periods, it passes otherwise.

Type Verification Description
-------------------------------------------------------------------------------
Procedure-based

Assertions Type
-------------------------------------------------------------------------------
Pass

