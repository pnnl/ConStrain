G36MinOAwEconomizer
====================================================================

Brief Description
-------------------------------------------------------------------------------
G36 minimum outdoor air control when economizer is active

Index Description
-------------------------------------------------------------------------------
   * Section 5.16 in Guideline 36-2021

Datapoints Description
-------------------------------------------------------------------------------
   * outdoor_air_temp: outdoor air temperature
   * economizer_high_limit_sp: economizer lockout high limit set point
   * outdoor_damper_command: outdoor air damper command
   * min_oa_p: minimum outdoor air damper position set point
   * min_oa_sp: minimum outdoor air flow rate setpoint
   * outdoor_air_flow: outdoor air flow rate
   * sys_mode: AHU system mode mode, enumeration of ['occupied', 'unoccupied', 'cooldown', 'warmup', 'setback', 'setup']

Assertions Description
-------------------------------------------------------------------------------
   * if not economizer_lockout(outdoor_air_temp, economizer_high_limit_sp) and sys_mode == 'occupied':

   *   if oudoor_damper_command >= MinOA-P and outdoor_air_flow >= MinOAsp:

   *     pass

   *   else:

   *     fail

   * else:

   *   untested

Type Verification Description
-------------------------------------------------------------------------------
Rule-based

Assertions Type
-------------------------------------------------------------------------------
Pass

