G36OutputChangeRateLimit
====================================================================

Brief Description
-------------------------------------------------------------------------------
G36 requirement of controller command change rate limit

Index Description
-------------------------------------------------------------------------------
   * Section 5.1.9 in Guideline 36-2021

Datapoints Description
-------------------------------------------------------------------------------
   * command: control command to be verified with command range being (0-100)
   * max_rate_of_change_per_min: control loop output maximum rate of change, default to 25.

Assertions Description
-------------------------------------------------------------------------------
   * if abs(command(current_t) - command(prev_t)) > max_rage_of_change_per_min and (current_t - prev_t <= 1 minute):

   *   fail

   * else:

   *   pass

Type Verification Description
-------------------------------------------------------------------------------
Rule-based

Assertions Type
-------------------------------------------------------------------------------
Pass

