### Brick API documentation

`Class BrickQueryCompliance`   

- `__init__(`_brick_schema_path: str_`, `_brick_instance_path: str_`)`    
Instantiate a `BrickQueryCompliance` class object and load specified brick schema and brick instance.   
    - **Parameters**  
        - **brick_schema_path**: `str` path to a brick schema to be used for query. The default location is `./resources/brick/Brick.ttl`.   
        - **brick_instance_path**: `str` path to a brick instance to be used for query. For now, only `.ttl` format is accepted.    
        - **query_statement_path**: `str` path to the query statements. The default path is `./resources/brick/query_statement.yml`.       
        - **datapoint_name_conversion_path**: `str` path to the datapoint conversion name saving yaml file. The default path is `./resources/brick/verification_datapoint_info.yml`.  
        - - **perform_reasoning**: `bool` argument whether reasoning is performed to the given instance. The default boolean value is False.  

- `validate_brick_instance()`   
Validate a brick instance against the brick schema.   
    - **Parameters**  
        - **brick_schema_path_str**: `str` path to the brick schema to be used for validation.  
    - **Returns**: i) `bool` whether the validation passes/fails, ii) `str` message from the validation process.       

- `get_applicable_verification_lib_items(`_verification_item_lib_name_:list_`)`    
Get applicable control verification library items among the `verification_item_lib_name` list from the given brick instance.        
    - **Parameters**  
        - **verification_item_lib_name**: `list` of `str` including verification item names to be tested. If empty list is provided, all the available verification library items are tested. 
    - **Returns**: `list` of `str` including available verification library item names from a brick instance.  

- `query_verification_case_datapoints(`_verification_item_lib_name: [str, list[str]]_`, `_energyplus_naming_assembly:bool = False_`, `_default_verification_case_values: dict = None_`)`  
Query datapoints required for given verification item lib.
    - **Parameters**  
        - **verification_item_lib_name**: `str` or `list` of `str` verification item library to be quried. If only one verification item library is quried, one `str` argument type is paased. If multiple verification item libraries are queried, `list` of `str` argument type is passed.    
        - **energyplus_naming_assembly**: `bool` (default: False) whether to convert the queried datapoints' name to EnergyPlus style variable name.   
        - **default_verification_case_values**: `dict` that has default key values. ("no", "run_simulation", "idf", "idd", "weather", "output", "ep_path", "expected_result", "parameters",) keys must exist.  
    - **Returns**: `list` of `dict`(s), queried results in verification case format. The return dict only includes `datapoints_source` and `verification_class` keys.    

- `query_with_customized_statement(`_custom_query_statement: str_`, `_energyplus_naming_assembly:bool = False_`, `_*verification_item_lib_name: str_`, `_default_verification_case_values: dict = None_`)`  
Query datapoints with a customized query statement. When implemented, the quality check of the `query_statement` is done by checking whether the number of queried variables are the same as the required number of data points in the verification library item.  
    - **Parameters**  
        - **custom_query_statement**: `str` query statement written from users.     
        - **verification_item_lib_name**: `str` verification library item of the `query_statement`.  
         - **energyplus_naming_assembly**: `bool` (default: True) whether to convert the queried datapoints' name to EnergyPlus style variable name. 
         - **default_verification_case_values**: `dict` that has default key values. ("no", "run_simulation", "idf", "idd", "weather", "output", "ep_path", "expected_result", "parameters",) keys must exist. 
    - **Returns**: `list` of `dict` of queried result in the verification case format. `str` message from the `query_statement`'s quality check result.    
    