LocalLoopSaturationReverseActingMax
====================================================================

Brief Description
-------------------------------------------------------------------------------
Local loop performance verification - reverse acting loop actuator maximum saturation

Datapoints Description
-------------------------------------------------------------------------------
   * feedback_sensor: feedback sensor reading of the subject to be controlled towards a set point
   * set_point: set point value
   * cmd: control command
   * cmd_max: control command range maximum value

Assertions Description
-------------------------------------------------------------------------------
   * If the sensed data values are consistently below its set point, and after a default of 1 hour, the control command is still not saturated to maximum, then the verification fails; Otherwise, it passes.

Type Verification Description
-------------------------------------------------------------------------------
Procedure-based

Assertions Type
-------------------------------------------------------------------------------
Pass

