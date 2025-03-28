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
        if current_p_press_static_sp < previous_p_press_static_sp:
            # Setpoint is being reduced
            return True
        elif any cmd_damper_vav > 90%:
            # At least one damper is nearly wide open
            return True
        else:
            # Neither condition is met - failing verification
            return False
    save current timestep as previous
```

### Data requirements

- p_press_static_sp: Duct static pressure setpoint
  - Data Value Unit: pressure
  - Data point Description: Duct static pressure setpoint
  - Data Point Affiliation: Fan control

- cmd_damper_vav: VAV damper command
  - Data Value Unit: percent
  - Data point Description: VAV damper command
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
