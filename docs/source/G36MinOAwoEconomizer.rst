G36MinOAwoEconomizer
====================================================================

Brief Description
-------------------------------------------------------------------------------
G36 minimum outdoor air control when economizer is in lockout

Index Description
-------------------------------------------------------------------------------
   * Section 5.16 in Guideline 36-2021

Datapoints Description
-------------------------------------------------------------------------------
   * outdoor_air_temp: outdoor air temperature
   * economizer_high_limit_sp: economizer lockout high limit set point
   * outdoor_damper_command: outdoor air damper command
   * return_damper_command: return air damper command
   * outdoor_air_flow: outdoor air flow rate
   * min_oa_sp: minimum outdoor air flow rate setpoint
   * sys_mode: AHU system mode mode, enumeration of ['occupied', 'unoccupied', 'cooldown', 'warmup', 'setback', 'setup']

Assertions Description
-------------------------------------------------------------------------------
   * if economizer_lockout(outdoor_air_temp, economizer_high_limit_sp) and sys_mode == 'occupied':

   *   if outdoor_air_flow < MinOAsp (continuously (e.g. fall below the sp for a consecutive 1 hr)):

   *     if outdoor_damper_command == 100 and return_damper_command == 0:

   *       pass

   *     else:

   *       fail

   *   elif outdoor_air_flow > MinOAsp (continuously):

   *     if outdoor_damper_command == 0 and return_damper_command == 100:

   *       pass

   *     else:

   *       fail

   *   else:

   *     pass (essentially untested yet)

   * else:

   *   untested

Type Verification Description
-------------------------------------------------------------------------------
Rule-based

Assertions Type
-------------------------------------------------------------------------------
Pass

