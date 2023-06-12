### Brick API documentation

`Class BrickQueryCompliance` <!-- Class name to be updated.-->

- [X] `__init__(`_brick_instance_path: str_`)`    
Instantiate a `BrickQueryCompliance` class object and load specified brick schema and brick instance.   
    - **Parameters**  
        - **brick_instance_path**: `str` path to a brick instance to be used for query. For now, only `.ttl` format is accepted.   

- [X] `validate_instance()`    <!-- consider using building motif, validation report: same, help us correct the model -->
Validate a brick instance against the brick schema.   
    - **Parameters**  
        - **brick_schema_path_str**: `str` path to the brick schema to be used for validation.  
    - **Returns**: i) `bool` whether the validation passes/fails, ii) `str` message from the validation process.       

- `get_applicable_verification_lib_items(`_verification_item_names:list_`, `_verification_lib_obj:obj_`)`    
Get applicable control verificaton cases among the `verification_item_names` list in the brick instance.        
    - **Parameters**  
        - **verification_item_names**: `list` of `str` including verification item names. If empty list is provided, the applicable 
        - **verification_lib_obj**: `obj` of the `VerificationLibrary` class. This argument is passed to make use of methods inside the `VerificationLibrary` class.  
    - **Returns**: `list` of `str` including available verification library item names from a brick instance.  

- [X] `query_verification_case_datapoints(`_verification_item_lib_name: [str, list[str]]_`, `_energyplus_naming_assembly:bool = False_`)`  
Query datapoints required for given verification item lib.
    - **Parameters**  
        - **verification_item_lib_name**: `str` or `list` of `str` verification item library to be quried. If only one verification item library is quried, one `str` argument type is paased. If multiple verification item libraries are queried, `list` of `str` argument type is passed.    
        - **energyplus_naming_assembly**: `bool` (default: False) whether to convert the queried datapoints' name to EnergyPlus style variable name.   
    - **Returns**: `list` of `dict`(s), queried results in verification case format. The return dict only includes `datapoints_source` and `verification_class` keys.    


- `query_with_customized_statement(`_query_statement: str_`, `_energyplus_naming_assembly:bool = False_`, `_*verification_item_lib_name: str_`)`  
Query datapoints with a customized query statement. When implemented, the quality check of the `query_statement` is done by checking whether the number of queried variables are the same as the required number of data points in the verification library item.  
    - **Parameters**  
        - **query_statement**: `str` query statement written from users.   
        - **energyplus_naming_assembly**: `bool` (default: False) whether to convert the queried datapoints' name to EnergyPlus style variable name.    
        - **verification_item_lib_name**: (optional) `str` verification library item of the `query_statement`. If this isn't provided, the `verification_class` key's value is set to empty.    
    - **Returns**: `list` of `dict` of queried result in the verification case format. `str` message from the `query_statement`'s quality check result.    


```python
import animate as an


# Instantiate BrickQueryCompliance obj
brick_instance_path = "./testing_brick_instance.ttl"
brick_obj = BrickQueryCompliance(brick_instance_path)


# check if the instance is valid 
brick_schema_path = "./brick.ttl" # Assumed the brick instance has all the classes/points needed for the SupplyAirTempReset and ZoneHeatSetpointMinimum verification lib items
result_bool, result_msg = brick_obj.validate_instance(brick_schema_path)

# expected `result_bool`: True
# expected `result_msg`: "Validation REport\nConforms: True\n"


# check which verification item library is applicable
verification_lib_obj = an.VerificationLibrary("./schema/library.json")
verification_item_names = ["SupplyAirTempReset", "AutomaticShutdown", "ServiceWaterHeatingSystemControl"] # find the applicable verification lib items only within this list

applicable_verification = brick_obj.get_applicable_verification_lib_items(verification_item_names, verification_lib_obj)

# expected `applicable_verification`: ["SupplyAirTempReset", "ZoneHeatSetpointMinimum"] # AutomaticShutdown isn't included b/c we assumed the brick instance only includes classes/points for SupplyAirTempReset and ZoneHeatSetpointMinimum


# query the `SupplyAirTempReset` verification item's data points
verification_item_lib_name = "SupplyAirTempReset" # assumed we only want to query the data points needed in `SupplyAirTempReset`
energyplus_naming_assembly = True

queried_result = brick_obj.query_verification_case_datapoints(verification_item_lib_name, energyplus_naming_assembly)

# expected `queried_result`:
# {"datapoints_source": {
#     "idf_output_variables": {
#         "T_sa_set": {
#             "subject": "VAV_1 Supply Equipment Outlet Node",
#             "variable": "System Node Setpoint Temperature",
#             "frequency": "detailed"
#         }
#     },
#     "parameters": {}
# },
# "verification_class": "SupplyAirTempReset"
# }
# }


# query with customized query statement (ZoneHeatSetpointMinimum)
query_statement = "SELECT ?heating_setpoint ?hvac_zone "
                  "WHERE {"
                            "?hvac_zone a brick:HVAC_Zone ."
                            "?heating_setpoint a brick:Zone_Air_Heating_Temperature_Setpoint ."
                            "?hvac_zone brick:hasPoint ?heating_setpoint ."
                        "}"
energyplus_naming_assembly = True

queried_result, msg = brick_obj.query_with_customized_statement(query_statement, energyplus_naming_assembly)

# expected `queried_result`:
# {"datapoints_source": {
#     "idf_output_variables": {
#         "T_wh_inlet": {
#             "subject": "BATHROOMS_ZN_1_FLR_1 SHW_DEFAULT",
#             "variable": "Water Use Equipment Mixed Water Temperature",
#             "frequency": "detailed"
#         }
#     },
#     "parameters": {}
# }
# }

# expected `msg`: "pass"
```
