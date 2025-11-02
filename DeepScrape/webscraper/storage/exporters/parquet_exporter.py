import pandas as pd
class ParquetExporter:
    """Write rows to Parquet (requires pyarrow)."""
    def write(self, rows, path):
        pd.DataFrame(rows).to_parquet(path, index=False)
