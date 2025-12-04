from typing import Dict, List, Any

class SchemaValidator:
    def validate_struct(self, entry: Dict[str, Any], req_fields: List[str]) -> bool:
        #vlaidate structure
        for key in req_fields:
            if key not in entry:
                print(f"[SchemaValidator] Missing required field: {key}")
                return False
        return True

    def check_fields(self, entry: Dict[str, Any], schema_spec: Dict[str, type]) -> Dict[str, Any]:
        #enfore type constraints and return dict w enforced types
        validated_entry = {}
        for key, req_type in schema_spec.items():
            if key not in entry:
                continue  
            
            value = entry[key]
            if not isinstance(value, req_type):
                try:
                    validated_entry[key] = req_type(value)
                    print(f"[SchemaValidator] Converted {key} to {req_type.__name__}")
                except Exception as e:
                    raise TypeError(
                        f"[SchemaValidator] Field '{key}' expected {req_type.__name__}, "
                        f"but got {type(value).__name__}. Error: {e}"
                    )
            else:
                validated_entry[key] = value
        return validated_entry
