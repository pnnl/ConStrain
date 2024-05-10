G36ReliefDamperStatus
====================================================================

Brief Description
-------------------------------------------------------------------------------
G36 relief dampers shall be enabled when the associated supply fan is proven on, and disabled otherwise.

Index Description
-------------------------------------------------------------------------------
   * Section 5.16.8.1 in Guideline 36-2021

Datapoints Description
-------------------------------------------------------------------------------
   * relief_damper_command: relief damper opening (0-100)
   * supply_fan_status: supply fan status (speed) [1, 0] (can be replaced by binary or numeric variables)

Assertions Description
-------------------------------------------------------------------------------
   * if relief_damper_command > 0 and supply_fan_status == 'on':

   *   pass

   * elif supply_fan_status == 'off' and relief_damper_command == 0:

   *   pass

   * else:

   *   fail

   * if not ['on', 'off'] in supply_fan_status:

   *   untested

Type Verification Description
-------------------------------------------------------------------------------
Rule-based

Assertions Type
-------------------------------------------------------------------------------
Pass

