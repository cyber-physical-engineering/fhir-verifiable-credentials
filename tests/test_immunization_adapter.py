from __future__ import annotations

import json
from pathlib import Path

from fhir_vc.core.crypto_signer import Ed25519Signer
from fhir_vc.core.vc_builder import VCBuilder
from fhir_vc.adapters.immunization import ImmunizationAdapter


def test_immunization_to_vc_smoke():
    data = json.loads(Path("examples/input/immunization_example.json").read_text())

    signer = Ed25519Signer.generate()
    builder = VCBuilder(issuer_did="did:web:hospital.example.com", signer=signer)

    vc = ImmunizationAdapter(builder).convert(data)
    out = vc.to_dict()

    assert out["issuer"] == "did:web:hospital.example.com"
    assert "proof" in out
    assert out["credentialSubject"]["type"] == "ImmunizationRecord"
