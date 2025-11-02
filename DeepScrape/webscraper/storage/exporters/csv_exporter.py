import pandas as pd
class CSVExporter:
    """Write rows to CSV."""
    def write(self, rows, path):
        pd.DataFrame(rows).to_csv(path, index=False)
