G36FreezeProtectionStage1
====================================================================

Brief Description
-------------------------------------------------------------------------------
G36 freeze protection stage 1 requirements

Index Description
-------------------------------------------------------------------------------
   * Section 5.16.12.1. in Guideline 36-2021

Datapoints Description
-------------------------------------------------------------------------------
   * supply_air_temp: supply air temperature
   * outdoor_damper_command: outdoor air damper
   * outdoor_damper_minimum: outdoor air damper minimum position

Assertions Description
-------------------------------------------------------------------------------
   * if supply_air_temp < 4.4 (continuously 5 minutes) and outdoor_damper_command > outdoor_damper_minimum:

   *   fail

   * elif outdoor_damper_command > outdoor_damper_minimum and not (supply_air_temp > 7 (continuously 5 minutes)):

   *   fail

   * else:

   *   pass

   * 

   * if never (supply_air_temp < 4.4 (continuously 5 minutes)):

   *   untested

Type Verification Description
-------------------------------------------------------------------------------
Rule-based

Assertions Type
-------------------------------------------------------------------------------
Pass

