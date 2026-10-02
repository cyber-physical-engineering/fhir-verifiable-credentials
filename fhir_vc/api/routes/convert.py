from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from ...adapters.immunization import ImmunizationAdapter
from ...core.crypto_signer import Ed25519Signer
from ...core.fhir_parser import parse_fhir_resource
from ...core.vc_builder import VCBuilder

router = APIRouter(prefix="", tags=["convert"])


class ConvertRequest(BaseModel):
    fhir: dict[str, Any]
    issuer_did: str
    # Demo API: it signs with a fresh key generated for each request.
    ephemeral_key: bool = True


@router.post("/convert")
def convert(req: ConvertRequest) -> dict[str, Any]:
    resource = parse_fhir_resource(req.fhir)

    if not req.ephemeral_key:
        return {
            "error": (
                "This demo API signs with a key generated per request. "
                "To sign with your own key, use the CLI with --key."
            )
        }
    signer = Ed25519Signer.generate()
    builder = VCBuilder(issuer_did=req.issuer_did, signer=signer)

    if resource.resource_type == "Immunization":
        vc = ImmunizationAdapter(builder).convert(resource.raw)
    else:
        return {"error": f"Unsupported resourceType: {resource.resource_type}"}

    return vc.to_dict()
