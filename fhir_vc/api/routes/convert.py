from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from ...core.crypto_signer import Ed25519Signer
from ...core.vc_builder import VCBuilder
from ...core.fhir_parser import parse_fhir_resource
from ...adapters.immunization import ImmunizationAdapter

router = APIRouter(prefix="", tags=["convert"])


class ConvertRequest(BaseModel):
    fhir: dict[str, Any]
    issuer_did: str
    # For demo purposes only: allow ephemeral signing
    ephemeral_key: bool = True


@router.post("/convert")
def convert(req: ConvertRequest) -> dict[str, Any]:
    resource = parse_fhir_resource(req.fhir)

    signer = Ed25519Signer.generate() if req.ephemeral_key else Ed25519Signer.generate()
    builder = VCBuilder(issuer_did=req.issuer_did, signer=signer)

    if resource.resource_type == "Immunization":
        vc = ImmunizationAdapter(builder).convert(resource.raw)
    else:
        return {"error": f"Unsupported resourceType: {resource.resource_type}"}

    return vc.to_dict()
