import json

VERIFICATION_CASES_SCHEMA_PATH = "schema/verification_cases.schema.json"
LIBRARY_PATH = "schema/library.json"

def load_verification_cases_schema():
    return load_json(VERIFICATION_CASES_SCHEMA_PATH)
    
def load_verification_cases_library():
    return load_json(LIBRARY_PATH)
    
def load_json(file_path):
    with open(file_path, "r") as file:
        return json.load(file)