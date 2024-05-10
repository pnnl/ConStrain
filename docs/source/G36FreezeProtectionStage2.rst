G36FreezeProtectionStage2
====================================================================

Brief Description
-------------------------------------------------------------------------------
G36 freeze protection stage 2 requirements

Index Description
-------------------------------------------------------------------------------
   * Section 5.16.12.2. in Guideline 36-2021

Datapoints Description
-------------------------------------------------------------------------------
   * supply_air_temp: supply air temperature
   * outdoor_damper_command: outdoor air damper

Assertions Description
-------------------------------------------------------------------------------
   * if supply_air_temp < 3.3 (continuously 5 minutes) and outdoor_damper_command > 0 (ever in the following hour):

   *   fail

   * else:

   *   pass

   * if never (supply_air_temp < 3.3 (continuously 5 minutes)):

   *   untested

Type Verification Description
-------------------------------------------------------------------------------
Rule-based

Assertions Type
-------------------------------------------------------------------------------
Pass

