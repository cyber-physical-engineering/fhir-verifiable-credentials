"""Builds and signs a credential in the W3C Verifiable Credentials shape.

A minimal builder for demos. The proof signs the credential as sorted-key JSON,
not a JSON-LD canonical form, and labels itself Ed25519Signature2020 without
being that suite. A real implementation needs JSON-LD canonicalization and a
standard proof suite.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

from .crypto_signer import CryptoSigner


@dataclass
class VerifiableCredential:
    """W3C Verifiable Credential structure (minimal)."""

    context: list[str]
    id: str
    type: list[str]
    issuer: str
    issuance_date: datetime
    expiration_date: datetime | None
    credential_subject: dict[str, Any]
    proof: dict[str, Any] | None = None
    credential_status: dict[str, Any] | None = None

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
    CONTEXT_V2 = (
        "https://www.w3.org/ns/credentials/v2",
        "https://w3id.org/security/suites/ed25519-2020/v1",
    )

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

        expiration = now + timedelta(days=valid_days) if valid_days else None

        return VerifiableCredential(
            context=list(self.CONTEXT_V2),
            id=f"urn:uuid:{uuid.uuid4()}",
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
