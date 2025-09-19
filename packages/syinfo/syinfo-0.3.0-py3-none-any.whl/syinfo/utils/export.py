"""Data export utilities for JSON and YAML formats."""

import json
from pathlib import Path
from typing import Any, Dict, Optional

from syinfo.exceptions import ValidationError


def _sanitize_for_yaml(value: Any) -> Any:
    """Recursively convert unsupported YAML objects to strings.

    Keeps standard Python primitives and containers intact.
    """
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, dict):
        return {str(k): _sanitize_for_yaml(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_sanitize_for_yaml(v) for v in value]
    return str(value)


def export_data(data: Dict[str, Any], format: str = "json", output_file: Optional[str] = None) -> str:
    """Export the given data to JSON or YAML.

    Args:
        data: Dictionary to export
        format: One of "json", "yaml", or "yml"
        output_file: Optional file path to write the exported content

    Returns:
        The exported string content

    Raises:
        ValidationError: If an unsupported format is provided
    """
    fmt = (format or "").strip().lower()
    if fmt not in {"json", "yaml", "yml"}:
        raise ValidationError(f"Unsupported export format: {format}")

    if fmt == "json":
        result = json.dumps(data, indent=2, default=str)
    else:
        import yaml  # type: ignore

        sanitized = _sanitize_for_yaml(data)
        result = yaml.dump(sanitized, default_flow_style=False)

    if output_file:
        path = Path(output_file)
        path.write_text(result, encoding="utf-8")

    return result


__all__ = ["export_data"]
