
## Results for Verification Case ID 1

### Pass/Fail check result
{'Sample #': 52560, 'Pass #': 16902, 'Fail #': 0, 'Untested #': 0, 'Verification Passed?': True}

### Result visualization

![./tests/api/VerificationCase1\All_plot_aio.png](.//VerificationCase1\All_plot_aio.png)

![./tests/api/VerificationCase1\All_plot_obo.png](.//VerificationCase1\All_plot_obo.png)

![./tests/api/VerificationCase1\Day_plot_aio.png](.//VerificationCase1\Day_plot_aio.png)

![./tests/api/VerificationCase1\Day_plot_obo.png](.//VerificationCase1\Day_plot_obo.png)


### Verification case definition
```
{
  "no": 1,
  "run_simulation": false,
  "simulation_IO": {
    "idf": "./tests/api/data/ASHRAE901_OfficeMedium_STD2019_Atlanta.idf",
    "idd": "./resources/Energy+V9_0_1.idd",
    "weather": "./weather/USA_GA_Atlanta-Hartsfield.Jackson.Intl.AP.722190_TMY3.epw",
    "output": "eplusout.csv",
    "ep_path": "C:\\EnergyPlusV9-0-1\\energyplus.exe"
  },
  "expected_result": "pass",
  "datapoints_source": {
    "idf_output_variables": {
      "o": {
        "subject": "BLDG_OCC_SCH_WO_SB",
        "variable": "Schedule Value",
        "frequency": "TimeStep"
      },
      "m_oa": {
        "subject": "CORE_BOTTOM VAV BOX COMPONENT",
        "variable": "Zone Air Terminal Outdoor Air Volume Flow Rate",
        "frequency": "TimeStep"
      },
      "m_ea": {
        "subject": "CORE_MID VAV BOX COMPONENT",
        "variable": "Zone Air Terminal Outdoor Air Volume Flow Rate",
        "frequency": "TimeStep"
      },
      "eco_onoff": {
        "subject": "PACU_VAV_BOT",
        "variable": "Air System Outdoor Air Economizer Status",
        "frequency": "TimeStep"
      }
    },
    "parameters": {
      "tol_o": 0.03,
      "tol_m_ea": 50,
      "tol_m_oa": 50
    }
  },
  "verification_class": "AutomaticOADamperControl",
  "case_id_in_suite": "cbd8796c-cf9e-11ed-8cba-ac74b154c918",
  "library_item_id": 17,
  "description_brief": "HVAC system shall be turned on and off everyday",
  "description_index": [
    "Section 6.4.3.4.2 in 90.1-2016"
  ],
  "description_datapoints": {
    "no_of_occ": "Number of occupants",
    "m_oa": "Air terminal outdoor air volume flow rate",
    "eco_onoff": "Air System Outdoor Air Economizer Status",
    "tol": "Tolerance for the num of occupants"
  },
  "description_assertions": [
    "if no_of_occ <= 0 + tol and m_ea + m_oa > 0 and eco_onoff = 0, then false else pass"
  ],
  "description_verification_type": "procedure-based",
  "assertions_type": "pass"
}
```

---

[Back](results.md)