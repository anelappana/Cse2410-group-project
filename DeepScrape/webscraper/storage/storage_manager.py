"""
StorageManager:
- Save rows (dicts) as CSV/JSON/Parquet based on config.
"""
import os
from webscraper.storage.exporters.csv_exporter import CSVExporter
from webscraper.storage.exporters.json_exporter import JSONExporter
from webscraper.storage.exporters.parquet_exporter import ParquetExporter

class StorageManager:
    def __init__(self, output_dir="data/exports", output_format="csv"):
        self.output_dir = output_dir
        self.output_format = output_format

    def save_data(self, rows, filename):
        os.makedirs(self.output_dir, exist_ok=True)
        path = os.path.join(self.output_dir, f"{filename}.{self.output_format}")
        if self.output_format == "csv":
            CSVExporter().write(rows, path)
        elif self.output_format == "json":
            JSONExporter().write(rows, path)
        else:
            ParquetExporter().write(rows, path)
        print(f"[export] {path}")
