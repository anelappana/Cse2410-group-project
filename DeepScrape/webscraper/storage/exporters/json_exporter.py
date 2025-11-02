import json
class JSONExporter:
    """Write rows to JSON."""
    def write(self, rows, path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(rows, f, ensure_ascii=False, indent=2)
