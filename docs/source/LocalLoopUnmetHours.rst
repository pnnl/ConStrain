LocalLoopUnmetHours
====================================================================

Brief Description
-------------------------------------------------------------------------------
Local loop performance verification - set point unmet hours

Datapoints Description
-------------------------------------------------------------------------------
   * feedback_sensor: feedback sensor reading of the subject to be controlled towards a set point
   * set_point: set point value

Assertions Description
-------------------------------------------------------------------------------
   * Instead of checking the number of samples among the whole data set for which the set points are not met, this verification checks the total accumulated time that the set points are not met within a threshold of 5% of abs(set_point) (if the set point is 0, then the threshold is default to be 0.01).

Type Verification Description
-------------------------------------------------------------------------------
Procedure-based

Assertions Type
-------------------------------------------------------------------------------
Pass

