G36FreezeProtectionStage3
====================================================================

Brief Description
-------------------------------------------------------------------------------
G36 freeze protection stage 3 (highest) requirements

Index Description
-------------------------------------------------------------------------------
   * Section 5.16.12.3. in Guideline 36-2021

Datapoints Description
-------------------------------------------------------------------------------
   * freeze_stat: (optional, set to False if system does not have it) binary freeze-stat
   * supply_air_temp: supply air temperature
   * outdoor_damper_command: outdoor air damper
   * supply_fan_status: supply fan status (speed): [1, 0] (can be replaced by binary or numeric variables)
   * return_fan_status: (optional, set to False if system does not have it) return fan status (speed)
   * relief_fan_status: (optional, set to False if system does not have it) relief fan status (speed)
   * cooling_coil_command: cooling coil command
   * heating_coil_command: heating coil command

Assertions Description
-------------------------------------------------------------------------------
   * if supply_air_temp < 3.3 (continuously 15 minutes) or

   *   supply_air_temp < 1 (continuously 5 minutes) or

   *   freeze_stat == True

   *   if not (

   *     outdoor_damper_command == 0 and

   *     supply_fan_status == 'off' and

   *     return_fan_status == 'off' and

   *     relief_fan_status == 'off' and

   *     cooling_coil_command == 100 and

   *     heating_coil_command > 0

   *   ):

   *     fail

   *   else:

   *     pass

   * if never (

   *   supply_air_temp < 3.3 (continuously 15 minutes) or

   *   supply_air_temp < 1 (continuously 5 minutes) or

   *   freeze_stat == True

   * ):

   *   untested

Type Verification Description
-------------------------------------------------------------------------------
Rule-based

Assertions Type
-------------------------------------------------------------------------------
Pass

