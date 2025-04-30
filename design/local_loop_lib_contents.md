# Local Loop Performance Verification Library Items

----

## Local Loop Performance Verification - Set Point Tracking

### Description

This verification checks the set point tracking ability of local control loops.

### Verification logic

With a threshold of 5% of abs(set_point) (if the set point is 0, then the threshold is default to be 0.01), if the number of samples of which the error is larger than this threshold is beyond 5% of number of all samples, then this verification fails; Otherwise, it passes.

### Data requirements

- feedback_sensor: feedback sensor reading of the subject to be controlled towards a set point
- set_point: set point value


## Local Loop Performance Verification - Set Point Unmet Hours

### Description

This verification checks the set point tracking ability of local control loops.

### Verification logic

Instead of checking the number of samples among the whole data set for which the set points are not met, this verification checks the total accumulated time that the set points are not met within a threshold of 5% of abs(set_point) (if the set point is 0, then the threshold is default to be 0.01).

If the accumulated time of unmet set point is beyond 5% of the whole duration the data covers, then this verification fails; otherwise, it passes.

### Data requirements

- feedback_sensor: feedback sensor reading of the subject to be controlled towards a set point
- set_point: set point value

## Local Loop Performance Verification - Direct Acting Loop Actuator Maximum Saturation

### Description

This verification checks that a direct acting control loop would saturate its actuator to maximum when the error is consistently above the set point [^1].

### Verification logic

If the sensed data values are consistently above its set point, and after a default of 1 hour, the control command is still not saturated to maximum, then the verification fails; Otherwise, it passes.

### Data requirements

- feedback_sensor: feedback sensor reading of the subject to be controlled towards a set point
- set_point: set point value
- cmd : control command
- cmd_max: control command range maximum value

## Local Loop Performance Verification - Direct Acting Loop Actuator Minimum Saturation

### Description

This verification checks that a direct acting control loop would saturate its actuator to minimum when the error is consistently below the set point [^1].

### Verification logic

If the sensed data values are consistently below its set point, and after a default of 1 hour, the control command is still not saturated to minimum, then the verification fails; Otherwise, it passes.

### Data requirements

- feedback_sensor: feedback sensor reading of the subject to be controlled towards a set point
- set_point: set point value
- cmd : control command
- cmd_min: control command range minimum value

## Local Loop Performance Verification - Reverse Acting Loop Actuator Maximum Saturation

### Description

This verification checks that a reverse acting control loop would saturate its actuator to maximum when the error is consistently below the set point [^1].

### Verification logic

If the sensed data values are consistently below its set point, and after a default of 1 hour, the control command is still not saturated to maximum, then the verification fails; Otherwise, it passes.

### Data requirements

- feedback_sensor: feedback sensor reading of the subject to be controlled towards a set point
- set_point: set point value
- cmd : control command
- cmd_max: control command range maximum value

## Local Loop Performance Verification - Reverse Acting Loop Actuator Minimum Saturation

### Description

This verification checks that a reverse acting control loop would saturate its actuator to minimum when the error is consistently above the set point [^1].

### Verification logic

If the sensed data values are consistently above its set point, and after a default of 1 hour, the control command is still not saturated to minimum, then the verification fails; Otherwise, it passes.

### Data requirements

- feedback_sensor: feedback sensor reading of the subject to be controlled towards a set point
- set_point: set point value
- cmd : control command
- cmd_min: control command range minimum value

<!-- ## Local Loop Performance Verification - Loop Activation Hunting

### Description

This verification checks if a loop has hunting behavior in terms of frequently activate and deactivate its actuator. -->

## Local Loop Performance Verification - Actuator Rate of Change

### Description

This verification checks if a local loop actuator has dramatic change of its actuating command. This verification is implemented as instructed by ASHRAE Guideline 36 2021 Section 5.1.9 in Verification Item `G36OutputChangeRateLimit`.



[^1]: Lei, Xuechen, Yan Chen, Mario Bergés, and Burcu Akinci. "Formalized control logic fault definition with ontological reasoning for air handling units." Automation in Construction 129 (2021): 103781.