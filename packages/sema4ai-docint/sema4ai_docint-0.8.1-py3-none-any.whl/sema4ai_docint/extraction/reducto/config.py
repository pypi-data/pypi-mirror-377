import copy
from typing import Any

# Reducto configuration
CUSTOM_CONFIG = {
    "array_extract": {"array_extract": {"enabled": True}},
    "table_enrich": {
        "experimental_options": {
            "enrich": {"mode": "table", "enabled": True},
            "layout_model": "beta",
            "merge_tables": True,
        }
    },
}


class ReductoConfig:
    """Simple class to provide Reducto configuration from embedded Python dict."""

    @classmethod
    def load_config(cls) -> dict[str, Any]:
        """Load the entire configuration."""
        return copy.deepcopy(CUSTOM_CONFIG)  # Return a deep copy to prevent modification
