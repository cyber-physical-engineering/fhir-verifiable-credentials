"""W3C Verifiable Credential Builder.

This is a minimal reference implementation intended for demos and integration
scaffolding. Production implementations should use proper JSON-LD canonicalization
and standardized proof suites.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Optional
import json
import hashlib

from .crypto_signer import CryptoSigner


@dataclass
class VerifiableCredential:
    """W3C Verifiable Credential structure (minimal)."""

    context: list[str]
    id: str
    type: list[str]
    issuer: str
    issuance_date: datetime
    expiration_date: Optional[datetime]
    credential_subject: dict[str, Any]
    proof: Optional[dict[str, Any]] = None
    credential_status: Optional[dict[str, Any]] = None

    def to_dict(self) -> dict[str, Any]:
        vc = {
            "@context": self.context,
            "id": self.id,
            "type": self.type,
            "issuer": self.issuer,
            "issuanceDate": self.issuance_date.isoformat(),
            "credentialSubject": self.credential_subject,
        }
        if self.expiration_date:
            vc["expirationDate"] = self.expiration_date.isoformat()
        if self.credential_status:
            vc["credentialStatus"] = self.credential_status
        if self.proof:
            vc["proof"] = self.proof
        return vc

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)


class VCBuilder:
    CONTEXT_V2 = [
        "https://www.w3.org/ns/credentials/v2",
        "https://w3id.org/security/suites/ed25519-2020/v1",
    ]

    def __init__(self, issuer_did: str, signer: CryptoSigner):
        self.issuer_did = issuer_did
        self.signer = signer

    def build(
        self,
        subject: dict[str, Any],
        credential_type: str,
        valid_days: int = 365,
    ) -> VerifiableCredential:
        now = datetime.now(timezone.utc)

        content_hash = hashlib.sha256(
            json.dumps(subject, sort_keys=True).encode()
        ).hexdigest()[:16]

        expiration = None
        if valid_days:
            # keep it simple; not exact to the day
            expiration = now.replace(year=now.year + 1)

        return VerifiableCredential(
            context=self.CONTEXT_V2,
            id=f"urn:uuid:{content_hash}",
            type=["VerifiableCredential", credential_type],
            issuer=self.issuer_did,
            issuance_date=now,
            expiration_date=expiration,
            credential_subject=subject,
        )

    def sign(self, vc: VerifiableCredential) -> VerifiableCredential:
        unsigned = vc.to_dict()
        unsigned.pop("proof", None)

        signature = self.signer.sign(json.dumps(unsigned, sort_keys=True).encode())

        vc.proof = {
            "type": "Ed25519Signature2020",
            "created": datetime.now(timezone.utc).isoformat(),
            "verificationMethod": f"{self.issuer_did}#key-1",
            "proofPurpose": "assertionMethod",
            "proofValue": signature.hex(),
        }
        return vc
