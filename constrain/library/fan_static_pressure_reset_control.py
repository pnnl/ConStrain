"""
### Description
The set point is reset lower until one zone damper is nearly wide open

### Code requirement

- Code Name: ASHRAE 90.1
- Code Year: 2016
- Code Section: 6.5.3.2 Fan Control
- Code Subsection: 6.5.3.2.3 VAV Set-Point Reset

### Verification Approach
- We aim to verify whether the static pressure setpoint is reset until one of the VAV boxes is nearly wide open.

### Verification logic
```
for row_num, (index, row) in df.iterrows:
    if row_num != 0:
        if p_set @ current time step < p_set @ previous time step:
            pass
        elif (d_vav_df> 0.9).any():
            pass
        else:
            fail
    else:
        Untested
    prev_index = index
```

### Data requirements
- p_set: Static pressure setpoint,
- d_VAV_x: VAV Damper x Position (includes all VAV dampers served by the system under test

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
                if self.df.at[prev_index, "p_set"] - self.df.at[
                    index, "p_set"
                ] > self.get_tolerance("pressure", "static"):
                    self.df.at[index, "result"] = True
                elif (d_vav_df.loc[index] > 0.9).any():
                    self.df.at[index, "result"] = True
                else:
                    self.df.at[index, "result"] = False
            else:
                self.df.at[index, "result"] = "Untested"
            prev_index = index

        self.result = self.df["result"]
