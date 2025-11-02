"""
SettingsManager:
- Loads YAML config and exposes accessors.
"""
import yaml
class SettingsManager:
    def __init__(self, path="config/settings.yaml"):
        with open(path, "r") as f:
            self._cfg = yaml.safe_load(f)
    def get_settings(self): return self._cfg
    def update_settings(self, new_settings: dict): self._cfg.update(new_settings or {})
    def validate_settings(self): return True
