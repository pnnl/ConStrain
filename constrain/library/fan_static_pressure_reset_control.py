"""
### Description

This verification aims to check if the static pressure setpoint is properly reset based on VAV damper positions. The setpoint should be reset lower until at least one zone damper is nearly wide open.

### Code requirement

- Code Name: ASHRAE 90.1
- Code Year: 2016
- Code Section: 6.5.3.2 Fan Control
- Code Subsection: 6.5.3.2.3 VAV Set-Point Reset

### Verification Approach

The verification monitors the static pressure setpoint and VAV damper positions over time. It checks that either the setpoint is being reduced, or at least one VAV damper is nearly wide open (>90% open). This ensures the system is operating at the minimum pressure needed.

### Verification Applicability

- Building Type(s): any
- Space Type(s): any
- System(s): VAV systems
- Climate Zone(s): any
- Component(s): supply fans, VAV boxes, static pressure sensors

### Verification Algorithm Pseudo Code

```
for each timestep:
    if first timestep:
        return "Untested"
    else:
        if current_pressure_setpoint < previous_pressure_setpoint:
            # Setpoint is being reduced
            return True
        elif any VAV damper position > 90%:
            # At least one damper is nearly wide open
            return True
        else:
            # Neither condition is met - failing verification
            return False
    save current timestep as previous
```

### Data requirements

- p_set: Static pressure setpoint
  - Data Value Unit: pressure
  - Data point Description: Supply air duct static pressure setpoint
  - Data Point Affiliation: Fan control

- d_VAV_x: VAV Damper Position
  - Data Value Unit: fraction (0-1)
  - Data point Description: Position of each VAV box damper served by the system
  - Data Point Affiliation: Zone control

"""

from constrain.checklib import RuleCheckBase


class FanStaticPressureResetControl(RuleCheckBase):
    points = [
        "p_set",
        "d_VAV_1",
        "d_VAV_2",
        "d_VAV_3",
        "d_VAV_4",
        "d_VAV_5",
    ]

    def verify(self):
        d_vav_points = ["d_VAV_1", "d_VAV_2", "d_VAV_3", "d_VAV_4", "d_VAV_5"]
        d_vav_df = self.df[d_vav_points]

        for row_num, (index, row) in enumerate(self.df.iterrows()):
            if row_num != 0:
                if self.df.at[index, "p_set"] < self.df.at[prev_index, "p_set"]:
                    self.df.at[index, "result"] = True
                elif (d_vav_df.loc[index] > 0.9).any():
                    self.df.at[index, "result"] = True
                else:
                    self.df.at[index, "result"] = False
            else:
                self.df.at[index, "result"] = "Untested"
            prev_index = index

        self.result = self.df["result"]
