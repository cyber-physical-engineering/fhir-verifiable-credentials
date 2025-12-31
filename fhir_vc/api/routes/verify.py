from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="", tags=["verify"])


class VerifyRequest(BaseModel):
    vc: dict[str, Any]


@router.post("/verify")
def verify(req: VerifyRequest) -> dict[str, Any]:
    # Minimal placeholder: validates presence of expected fields.
    vc = req.vc
    required = ["@context", "type", "issuer", "issuanceDate", "credentialSubject", "proof"]
    missing = [k for k in required if k not in vc]
    if missing:
        return {"valid": False, "missing": missing}
    return {"valid": True}
