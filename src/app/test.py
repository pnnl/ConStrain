
{
    "Load data": {
      "Type": "MethodCall",
      "MethodCall": "DataProcessing",
      "Parameters": {
        "data_path": "./tests/api/data/data_eplus.csv",
        "data_source": "EnergyPlus"
      },
      "Payloads": {
        "data": "$.data",
        "data_processing_obj": "$"
      },
      "Next": "Slice data",
      "Start": "True"
    }
}

{
    "Slice data": {
      "Type": "MethodCall",
      "MethodCall": "Payloads['data_processing_obj'].slice",
      "Parameters": {
        "start_time": {
          "Type": "Embedded MethodCall",
          "MethodCall": "datetime.datetime",
          "Parameters": [
            2000,
            1,
            1,
            12
          ]
        },
        "end_time": {
          "Type": "Embedded MethodCall",
          "MethodCall": "datetime.datetime",
          "Parameters": [
            2000,
            1,
            1,
            13
          ]
        }
      },
      "Payloads": {
        "sliced_data": "$"
      },
      "Next": "Data Length Check"
    }
}

{
    "Data Length Check": {
      "Type": "Choice",
      "Choices": [
        {
          "Value": "len(Payloads['sliced_data']) > 1",
          "Equals": "True",
          "Next": "Initialize verification object"
        },
        {
          "ANY": [
            {
              "Value": 1,
              "Equals": "True"
            },
            {
              "Value": "'data' in Payloads",
              "Equals": "True"
            },
            {
              "Value": "'fake_data' in Payloads",
              "Equals": "False"
            }
          ],
          "Next": "Run verification"
        }
      ],
      "Default": "Reporting"
    }
}

{
    "Initialize verification object": {
      "Type": "MethodCall",
      "MethodCall": "Verification",
      "Parameters": {
        "verification_cases_path": "x/yy.json"
      },
      "Payloads": {
        "verification": "$"
      },
      "Next": "Run verification"
    }
}
    
{
    "Run verification": {
      "Type": "MethodCall",
      "MethodCall": "Payloads['verification'].run",
      "Parameters": {},
      "Payloads": {
        "verification_md": "$.md",
        "verification_flag": "$.check_bool"
      },
      "Next": "Reporting"
    }
}

{
    "Reporting": {
      "Type": "MethodCall",
      "MethodCall": "Reporting",
      "Parameters": {
        "verification_md": "Payloads['verification_md']",
        "report_path": "x/yy.md",
        "report_format": "markdown"
      },
      "Payloads": {
        "verification": "$"
      },
      "End": "True"
    }   
}