"""
### Description

Section 6.4.3.4.2 Shutoff Damper Controls 
- All outdoor air intake and exhaust systems shall be equipped with motorized dampers that will automatically shut when the systems or spaces served are not in use. 
Ventilation outdoor air and exhaust/relief dampers shall be capable of and configured to automatically shut off during preoccupancy building warm-up, cooldown, and setback, except when ventilation reduces energy costs or when ventilation must be supplied to meet code requirements.

### Code requirement

- Code Name: ASHRAE 90.1
- Code Year: 2016
- Code Section: 6.4.3.4.2 Shutoff Damper Controls

### Verification Approach

The verification checks that when a space is unoccupied and the economizer is not active, the outdoor air and exhaust air dampers should be closed (flow rates near zero). The verification passes if this condition is met.

### Verification Applicability

- Building Type(s): any
- Space Type(s): any
- System(s): HVAC systems with outdoor air dampers
- Climate Zone(s): any
- Component(s): outdoor air dampers, exhaust air dampers

### Verification Algorithm Pseudo Code

```
if number_occupants <= 0 and flow_volumetric_air_exhaust + flow_volumetric_air_outdoor > 0 and status_economizer = 0
    return false
else
    return pass
```

### Data requirements

- number_occupants: Number of occupants
  - Data Value Unit: count
  - Data Point Affiliation: Zone occupancy

- flow_volumetric_air_outdoor: System outdoor air volume flow rate
  - Data Value Unit: volumetric flow rate
  - Data Point Affiliation: System ventilation

- flow_volumetric_air_exhaust: System exhaust air volume flow rate
  - Data Value Unit: volumetric flow rate
  - Data Point Affiliation: System ventilation

- status_economizer: System air-side economizer status
  - Data Value Unit: binary
  - Data Point Affiliation: System operation

"""

from constrain.checklib import RuleCheckBase


class AutomaticOADamperControl(RuleCheckBase):
    points = [
        "number_occupants",
        "status_economizer",
        "flow_volumetric_air_outdoor",
        "flow_volumetric_air_exhaust",
    ]

    def automatic_oa_damper_check(self, data):
        if data["number_occupants"] < self.get_tolerance("ratio", "occupancy"):
            if data["status_economizer"] == 0 and (
                float(data["flow_volumetric_air_outdoor"])
                >= self.get_tolerance("airflow", "outdoor_air")
                or float(data["flow_volumetric_air_exhaust"])
                >= self.get_tolerance("airflow", "exhaust_air")
            ):
                return False
            else:
                return True
        else:
            return "Untested"

    def verify(self):
        self.result = self.df.apply(lambda d: self.automatic_oa_damper_check(d), axis=1)
