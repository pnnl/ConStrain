# Control Verification Algorithm -- HPWH_sizing

Author: _Yun Joon Jung, Jeremy Lerond_     
Updated: _08/22/2024_

<!--
- Recommend formatting markdown with prettier https://prettier.io/ (available as vscode extension)
- `---` are added for easy presentation later (with things like slidev https://sli.dev/ )
 -->

---

## Verification Name

_HPWH_sizing_

## Verification Description

_TBD_  

## Code Requirements

### Code requirement

**Code Name:** _N/A_  
**Code Year:** _N/A_  
**Code Section:** _N/A_       
**Code Subsection:** _N/A_  

---

## Verification Approaches

### Verification Approach   

_We aim to verify this control verification item with heating rate from hpwh coils._

---

#### Verification Type

_rule-based_

#### Verification Applicability

- **Building Type(s):** _any_
- **Space Type(s):** _any_
- **System(s):**
  _1. Heat pump Water Heater system with a stratified tank._
- **Climate Zone(s):** _any_
- **Component(s):**

---

#### Verification Algorithm Data Points

- _T_amb_
  - Data Value Unit: deg C
  - Data point Description: _Environment:Site Outdoor Air Drybulb Temperature_
  - Data Point Affiliation: _Outdoor environment_

- _HeatingRate_dx_coil_
  - Data Value Unit: _W_
  - Data point Description: _Coil Total Water Heating Rate_
  - Data Point Affiliation: _heat pump water heater_

- _HeatingRate_waterheater1_
  - Data Value Unit: _W_
  - Data point Description: _Water Heater Heater 1 Heating Rate_
  - Data Point Affiliation: _heat pump water heater_

- _HeatingRate_waterheater2_
  - Data Value Unit: _W_
  - Data point Description: _Water Heater Heater 2 Heating Rate_
  - Data Point Affiliation: _heat pump water heater_

- _T_amb_parameter_
  - Data Value Unit: deg C
  - Data point Description: _Environment:Site Outdoor Air Drybulb Temperature parameter_
  - Data Point Affiliation: _Outdoor environment_


#### Verification Algorithm Description

_The algorithm verifies whether hpwh DX coil can achieve 100% heating rate at every time step._

#### Verification Algorithm Pseudo Code

```
total_load = hpwh_load + HeatingRate_waterheater1 + HeatingRate_waterheater2

if T_amb < T_amb_parameter or total_load == 0:
  untested
else if  hpwh_load / total_load >= 1
  pass
else
  fail
```

---

## Unit Tests

- _Provide a synthetic dataset that allow us to test both outcomes shown above: false and true._

---

## Implementation Description

_WIP_

#### Annotations
