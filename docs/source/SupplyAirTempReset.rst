SupplyAirTempReset
====================================================================

Brief Description
-------------------------------------------------------------------------------
Cooling supply air temperature reset scale (25%)

Detailed Description
-------------------------------------------------------------------------------
Multiple zone hvac systems must include controls that automatically reset the supply air temperature in response to representative building loads, or to outdoor air temperature. the controls shall reset the supply air temperature at least 25% of the difference between the design supply air temperature and the design room air temperature. controls that adjust the reset based on zone humidity are allowed. zones that are expected to experience relatively constant loads, such as electronic equipment rooms, shall be designed for the fully reset supply temperature.

Index Description
-------------------------------------------------------------------------------
   * Section 6.5.3.5 in 90.1-2016

Datapoints Description
-------------------------------------------------------------------------------
   * T_sa_set: AHU supply air temperature setpoint
   * T_z_coo: Design zone cooling air temperature

Assertions Description
-------------------------------------------------------------------------------
   * Max(T_sa_set) - Min(T_sa_set) >= (T_z_coo - Min(T_sa_set)) * 0.25

Type Verification Description
-------------------------------------------------------------------------------
Rule-based

Assertions Type
-------------------------------------------------------------------------------
Pass

