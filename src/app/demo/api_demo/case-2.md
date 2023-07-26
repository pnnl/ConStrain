
## Results for Verification Case ID 2

### Pass/Fail check result
{'Sample #': 8583, 'Pass #': 8583, 'Fail #': 0, 'Verification Passed?': True}

### Result visualization

![./demo/api_demo/VerificationCase2\All_plot_aio.png](.//VerificationCase2\All_plot_aio.png)

![./demo/api_demo/VerificationCase2\All_plot_obo.png](.//VerificationCase2\All_plot_obo.png)

![./demo/api_demo/VerificationCase2\All_samples_distribution_of_T_sa_set.png](.//VerificationCase2\All_samples_distribution_of_T_sa_set.png)

![./demo/api_demo/VerificationCase2\Day_plot_aio.png](.//VerificationCase2\Day_plot_aio.png)

![./demo/api_demo/VerificationCase2\Day_plot_obo.png](.//VerificationCase2\Day_plot_obo.png)


### Verification case definition
```
{
  "no": 2,
  "run_simulation": false,
  "simulation_IO": {
    "idf": "./test_cases/doe_prototype_cases/ASHRAE901_Hospital_STD2019_Atlanta.idf",
    "idd": "./resources/Energy+V9_0_1.idd",
    "weather": "./weather/USA_GA_Atlanta-Hartsfield.Jackson.Intl.AP.722190_TMY3.epw",
    "output": "./demo/api_demo/demo_dataset.csv",
    "ep_path": "C:\\EnergyPlusV9-0-1\\energyplus.exe"
  },
  "expected_result": "pass",
  "datapoints_source": {
    "idf_output_variables": {
      "T_sa_set": {
        "subject": "VAV_2 Supply Equipment Outlet Node",
        "variable": "System Node Setpoint Temperature",
        "frequency": "detailed"
      }
    },
    "parameters": {
      "T_z_coo": 24.0
    }
  },
  "verification_class": "SupplyAirTempReset",
  "case_id_in_suite": "a6510466-2bd7-11ee-b91c-508140fcb858",
  "library_item_id": 1,
  "description_brief": "Cooling supply air temperature reset scale (25%)",
  "description_detail": "Multiple zone HVAC systems must include controls that automatically reset the supply air temperature in response to representative building loads, or to outdoor air temperature. The controls shall reset the supply air temperature at least 25% of the difference between the design supply air temperature and the design room air temperature. Controls that adjust the reset based on zone humidity are allowed. Zones that are expected to experience relatively constant loads, such as electronic equipment rooms, shall be designed for the fully reset supply temperature.",
  "description_index": [
    "Section 6.5.3.5 in 90.1-2016"
  ],
  "description_datapoints": {
    "T_sa_set": "AHU supply air temperature setpoint",
    "T_z_coo": "Design zone cooling air temperature"
  },
  "description_assertions": [
    "Max(T_sa_set) - Min(T_sa_set) >= (T_z_coo - Min(T_sa_set)) * 0.25"
  ],
  "description_verification_type": "rule-based",
  "assertions_type": "pass"
}
```

---

[Back](results.md)