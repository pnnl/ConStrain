G36SupplyFanStatus
====================================================================

Brief Description
-------------------------------------------------------------------------------
G36 supply fan on/off requirements

Index Description
-------------------------------------------------------------------------------
   * Section 5.16.1.1. in Guideline 36-2021

Datapoints Description
-------------------------------------------------------------------------------
   * sys_mode: AHU system mode mode, enumeration of ['occupied', 'unoccupied', 'cooldown', 'warmup', 'setback', 'setup']
   * has_reheat_box_on_perimeter_zones: binary flag of If there are any VAV-reheat boxes on perimeter zones.
   * supply_fan_status: supply fan status (speed) [1, 0] (can be replaced by binary or numeric variables)

Assertions Description
-------------------------------------------------------------------------------
   * if has_reheat_box_on_perimeter_zones == True:

   *     if sys_mode != 'unoccupied' and supply_fan_status == 'off':

   *         fail

   * 

   * else:

   *     if sys_mode in ['occupied', 'setup', 'cooldown'] and supply_fan_staus == 'off':

   *         fail

   * 

   * if ['occupied', 'unoccupied'] in sys_mode:

   *   pass

   * else:

   *   untested

Type Verification Description
-------------------------------------------------------------------------------
Rule-based

Assertions Type
-------------------------------------------------------------------------------
Pass

