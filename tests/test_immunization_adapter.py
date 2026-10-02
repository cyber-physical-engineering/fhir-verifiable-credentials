from __future__ import annotations

import json
from datetime import timedelta
from pathlib import Path

from cryptography.exceptions import InvalidSignature

from fhir_vc.adapters.immunization import ImmunizationAdapter
from fhir_vc.core.crypto_signer import Ed25519Signer
from fhir_vc.core.vc_builder import VCBuilder


def test_immunization_to_vc_smoke():
    data = json.loads(Path("examples/input/immunization_example.json").read_text())

    signer = Ed25519Signer.generate()
    builder = VCBuilder(issuer_did="did:web:hospital.example.com", signer=signer)

    vc = ImmunizationAdapter(builder).convert(data)
    out = vc.to_dict()

    assert out["issuer"] == "did:web:hospital.example.com"
    assert "proof" in out
    assert out["credentialSubject"]["type"] == "ImmunizationRecord"


def test_signature_verifies_and_detects_changes():
    data = json.loads(Path("examples/input/immunization_example.json").read_text())

    signer = Ed25519Signer.generate()
    builder = VCBuilder(issuer_did="did:web:hospital.example.com", signer=signer)
    vc = ImmunizationAdapter(builder).convert(data).to_dict()

    proof = vc.pop("proof")
    signature = bytes.fromhex(proof["proofValue"])
    public_key = signer.private_key.public_key()

    # The proof signs the credential (without its proof) as sorted-key JSON.
    public_key.verify(signature, json.dumps(vc, sort_keys=True).encode())

    vc["credentialSubject"]["lotNumber"] = "LOT-CHANGED"
    try:
        public_key.verify(signature, json.dumps(vc, sort_keys=True).encode())
    except InvalidSignature:
        pass
    else:
        raise AssertionError("a changed credential still verified")


def test_expiration_follows_valid_days():
    builder = VCBuilder(issuer_did="did:web:example.com", signer=Ed25519Signer.generate())
    vc = builder.build(subject={"type": "Test"}, credential_type="TestCredential", valid_days=30)
    assert vc.expiration_date is not None
    assert vc.expiration_date - vc.issuance_date == timedelta(days=30)
