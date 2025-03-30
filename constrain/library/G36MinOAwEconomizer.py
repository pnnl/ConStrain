"""
### Description

Section 5.16 interpretation:
- With Relief damper or relief fan
  - when economizer control is not in lockout, and actual damper positions are controlled by the SAT control loop. Above only set the lower limit for OA damper. Track MinOAsp with a reverse-acting loop and map output to
    - OA (economizer) damper minimum position MinOA-P
    - return air damper maximum position MaxRA-P
  - when economizer is in lockout for more than 10 minutes (exceeding economizer high limit conditions in Section 5.1.17), the dampers are controlled to meet minimum OA requirements
    - fully open RA damper
    - set MaxOA-P = MinOA-P, control OA damper to meet MinOAsp
    - modulate RA damper to maintain MinOAsp (return air damper position equals to MaxRA-P)

### Code requirement

- Code Name: ASHRAE Guideline 36
- Code Year: 2021
- Code Section: 5.16 Air Handling Unit and Relief Fan Control Sequences
- Code Subsection: Minimum Outdoor Air Control with Economizer

### Verification Approach

The verification checks that during occupied periods when economizer is not in lockout, the outdoor air damper position and flow rate remain at or above their minimum setpoints. The actual damper modulation for temperature control is handled by the supply air temperature control loop.

### Verification Applicability

- Building Type(s): any
- Space Type(s): any
- System(s): Air handling units with economizers
- Climate Zone(s): any
- Component(s): outdoor air dampers, airflow sensors

### Verification Algorithm Pseudo Code

```python
if not economizer_lockout(temperature_air_outdoor, temperature_air_economizer_limit) and mode_system == 'occupied':
    if position_damper_air_outdoor >= position_damper_air_outdoor_min and flow_volumetric_air_outdoor >= flow_volumetric_air_outdoor_setpoint_min:
        pass
    else:
        fail
else:
    untested
```

### Data requirements

- temperature_air_outdoor: Outdoor air temperature
  - Data Value Unit: °C
  - Data Point Affiliation: Environmental conditions

- temperature_air_economizer_limit: Economizer high limit temperature
  - Data Value Unit: °C
  - Data Point Affiliation: Economizer control

- position_damper_air_outdoor: Outdoor air damper position
  - Data Value Unit: percent
  - Data Point Affiliation: Air handling unit

- position_damper_air_outdoor_min: Minimum outdoor air damper position
  - Data Value Unit: percent
  - Data Point Affiliation: Air handling unit

- flow_volumetric_air_outdoor_setpoint_min: Minimum outdoor airflow setpoint
  - Data Value Unit: volumetric flow rate
  - Data Point Affiliation: Air handling unit

- flow_volumetric_air_outdoor: Outdoor airflow
  - Data Value Unit: volumetric flow rate
  - Data Point Affiliation: Air handling unit

- mode_system: System mode (If mode_system is not "occupied", this verification item results fall into ""Untested)
  - Data Value Unit: enumeration
  - Data Point Affiliation: System control

"""

from constrain.checklib import RuleCheckBase


class G36MinOAwEconomizer(RuleCheckBase):
    points = [
        "temperature_air_outdoor",
        "temperature_air_economizer_limit",
        "position_damper_air_outdoor",
        "position_damper_air_outdoor_min",
        "flow_volumetric_air_outdoor",
        "flow_volumetric_air_outdoor_setpoint_min",
        "mode_system",
    ]

    def economizer_lockout(self, t_oa, t_economizer_limit):
        if t_oa > t_economizer_limit:
            return True
        else:
            return False

    def ts_verify_logic(self, t):
        if (
            not self.economizer_lockout(
                t["temperature_air_outdoor"], t["temperature_air_economizer_limit"]
            )
        ) and (t["mode_system"].strip().lower() == "occupied"):
            if (
                t["position_damper_air_outdoor"]
                >= t["position_damper_air_outdoor_min"]
                - self.get_tolerance("damper", "position")
            ) and (
                t["flow_volumetric_air_outdoor"]
                >= t["flow_volumetric_air_outdoor_setpoint_min"]
                - self.get_tolerance("airflow", "outdoor_air")
            ):
                return True
            else:
                return False
        else:
            return "Untested"

    def verify(self):
        self.result = self.df.apply(lambda t: self.ts_verify_logic(t), axis=1)
