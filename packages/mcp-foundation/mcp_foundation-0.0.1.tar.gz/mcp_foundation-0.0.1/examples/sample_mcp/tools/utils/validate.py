"""Validation utilities for MCP tools."""

from typing import Any
import logging

logger = logging.getLogger(__name__)


def validate_required_param(param_name: str, value: Any) -> Any:
    """Validate that a required parameter is provided."""
    if not value:
        raise ValueError(f"{param_name} parameter is required")
    return value
