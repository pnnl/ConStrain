GuestRoomControlTemp
====================================================================

Brief Description
-------------------------------------------------------------------------------
Verify whether there is guest room temperature control during operation hours

Index Description
-------------------------------------------------------------------------------
   * Section 6.4.3.3.5 in 90.1-2016

Datapoints Description
-------------------------------------------------------------------------------
   * T_z_hea_set: Zone Thermostat Heating Setpoint Temperature
   * T_z_coo_set: Zone Thermostat Cooling Setpoint Temperature
   * O_sch: Occupant Schedule
   * tol_occ: Tolerence for Occupant Schedule
   * tol_temp: Tolerance for Temperature

Assertions Description
-------------------------------------------------------------------------------
   * Check the two different temperature control logics when the room is/isn't rented out

Type Verification Description
-------------------------------------------------------------------------------
Rule-based

Assertions Type
-------------------------------------------------------------------------------
Pass

