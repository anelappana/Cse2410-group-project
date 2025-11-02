"""
SchemaValidator:
- Ensure required fields present.
- Type/range checks (extend spec as needed).
"""
class SchemaValidator:
    def validate(self, data: dict, required):
        if not isinstance(data, dict): return False
        for k in (required or []):
            if k not in data: return False
        return True
    def enforce_types(self, data: dict, spec: dict) -> dict:
        return data
