from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class FHIRResource:
    resource_type: str
    raw: dict[str, Any]


def parse_fhir_resource(data: dict[str, Any]) -> FHIRResource:
    """Very small parser/validator.

    Real-world integrations should validate against official FHIR schemas.
    """
    rt = data.get("resourceType")
    if not rt or not isinstance(rt, str):
        raise ValueError("FHIR resource missing 'resourceType'")
    return FHIRResource(resource_type=rt, raw=data)
