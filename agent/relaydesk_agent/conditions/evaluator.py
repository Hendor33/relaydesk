from pathlib import Path
from typing import Any

class ConditionEvaluator:
    def evaluate(self, condition_type: str, config: dict[str, Any], context: dict[str, Any]) -> bool:
        if condition_type != "file_extension":
            raise ValueError(f"Unsupported condition: {condition_type}")
        operator = config.get("operator", "equals")
        if operator != "equals":
            raise ValueError(f"Unsupported operator: {operator}")
        expected = str(config.get("value", "")).lower()
        if expected and not expected.startswith("."):
            expected = "." + expected
        actual = str(context["file"].get("extension") or Path(context["file"]["path"]).suffix).lower()
        return actual == expected
