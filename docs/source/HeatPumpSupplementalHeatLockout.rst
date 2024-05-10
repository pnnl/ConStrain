HeatPumpSupplementalHeatLockout
====================================================================

Brief Description
-------------------------------------------------------------------------------
Supplemental heating coil should be off when the heat pump can meet the load by itself

Index Description
-------------------------------------------------------------------------------
   * Section 6.4.3.5 Heat Pump Auxiliary Heat Control and 6.3.2.h Criteria in 90.1-2016

Datapoints Description
-------------------------------------------------------------------------------
   * C_ref: Heating Coil Reference Capacity
   * L_op: Heating Coil Runtime Fraction
   * C_t_mod: Heating Coil Heating Rate
   * P_supp_ht: Heating Coil Gas Rate
   * C_ff_mod: Heating Capacity Function of Flow Fraction Curve
   * L_defrost: Defrost load on the heating coil

Assertions Description
-------------------------------------------------------------------------------
   * If C_ref * C_t_mod >= L_op and P_supp_ht == 0 then pass else fail

Type Verification Description
-------------------------------------------------------------------------------
Rule-based

Assertions Type
-------------------------------------------------------------------------------
Pass

