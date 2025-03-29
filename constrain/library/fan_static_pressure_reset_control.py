"""
### Description

Section 6.5.3.2.3 VAV Set-Point Reset
- For multiple-zone VAV systems having a total fan system motor nameplate horsepower exceeding 5 hp with DDC of individual zones reporting to the central control panel, static pressure set 
point shall be reset based on the zone requiring the most pressure; i.e., the set point is reset lower until one zone damper is nearly wide open.

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
        if current_pressure_static_setpoint < previous_pressure_static_setpoint:
            # Setpoint is being reduced
            return True
        elif any pos_damper_vav_* > 90%:
            # At least one damper is nearly wide open
            return True
        else:
            # Neither condition is met - failing verification
            return False
    save current timestep as previous
```

### Data requirements

- pressure_static_setpoint: Duct static pressure setpoint
  - Data Value Unit: pressure
  - Data Point Affiliation: Fan control

- pos_damper_vav_x: VAV damper position
  - Data Value Unit: percent
  - Data Point Affiliation: Zone control

"""

from constrain.checklib import RuleCheckBase


class FanStaticPressureResetControl(RuleCheckBase):
    points = [
        "pressure_static_setpoint",
        "pos_damper_vav_1",
        "pos_damper_vav_2",
        "pos_damper_vav_3",
        "pos_damper_vav_4",
        "pos_damper_vav_5",
    ]

    def verify(self):
        vav_points = [
            "pos_damper_vav_1",
            "pos_damper_vav_2",
            "pos_damper_vav_3",
            "pos_damper_vav_4",
            "pos_damper_vav_5",
        ]
        vav_df = self.df[vav_points]

        for row_num, (index, row) in enumerate(self.df.iterrows()):
            if row_num != 0:
                if self.df.at[prev_index, "pressure_static_setpoint"] - self.df.at[
                    index, "pressure_static_setpoint"
                ] > self.get_tolerance("pressure", "static"):
                    self.df.at[index, "result"] = True
                elif (vav_df.loc[index] > 0.9).any():
                    self.df.at[index, "result"] = True
                else:
                    self.df.at[index, "result"] = False
            else:
                self.df.at[index, "result"] = "Untested"
            prev_index = index

        self.result = self.df["result"]
