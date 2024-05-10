HeatRejectionFanVariableFlowControlsCells
====================================================================

Brief Description
-------------------------------------------------------------------------------
Heat rejection fan variable flow controls cells

Index Description
-------------------------------------------------------------------------------
   * Section 6.5.5.2.2 in 90.1-2016

Datapoints Description
-------------------------------------------------------------------------------
   * ct_op_cells: Number of operating cooling tower cells
   * ct_cells: Number of cooling tower cells
   * ct_m: Cooling tower mass flow rate
   * ct_m_des: Cooling tower design mass flow rate
   * min_flow_frac_per_cell: Minimum flow fraction per cooling tower cell
   * ct_P_fan: Cooling tower fan power

Assertions Description
-------------------------------------------------------------------------------
   * if the number of operating cooling tower cells is equal to the maximum number of cooling tower cells then pass else fail

Type Verification Description
-------------------------------------------------------------------------------
Procedure-based

Assertions Type
-------------------------------------------------------------------------------
Pass

