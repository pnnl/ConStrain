# Control Verification Algorithm -- DHW_tank_temperature

Author: _Yun Joon Jung, Jeremy Lerond_     
Updated: _08/22/2024_

<!--
- Recommend formatting markdown with prettier https://prettier.io/ (available as vscode extension)
- `---` are added for easy presentation later (with things like slidev https://sli.dev/ )
 -->

---

## Verification Name

_DHW_tank_temperature_

## Verification Description

_TBD_  

## Code Requirements

### Code requirement

**Code Name:** _NA_  
**Code Year:** _NA_  
**Code Section:** _NA_       
**Code Subsection:** _NA_  

---

## Verification Approaches

### Verification Approach   

_We aim to verify this control verification item by examing water temperature in the domestic hot water tank._

---

#### Verification Type

_rule-based_

#### Verification Applicability

- **Building Type(s):** _any_
- **Space Type(s):** _any_
- **System(s):**
  _1. domestic hot water system._
- **Climate Zone(s):** _any_
- **Component(s):**

---

#### Verification Algorithm Data Points
- _T_dhw_
  - Data Value Unit: _deg C_
  - Data point Description: _Water Heater Temperature_
  - Data Point Affiliation: _Domestic Hot Water System_

- _T_dhw_deadband_
  - Data Value Unit: _deg C_
  - Data point Description: _Water Heater Temperature Temperature Deadband_
  - Data Point Affiliation: _Domestic Hot Water System_

- _T_dhw_design_parameter_
  - Data Value Unit: _deg C_
  - Data point Description: _Water Heater Temperature Parameter_
  - Data Point Affiliation: _Domestic Hot Water System_

#### Verification Algorithm Description

_The algorithm verifies whether water temperature in the domestic hot water tank is within the deadband._

#### Verification Algorithm Pseudo Code

```
If abs(T_dhw_outlet - T_design_water_outlet_parameter) <= 0.5 * T_dhw_outlet_deadband  
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
