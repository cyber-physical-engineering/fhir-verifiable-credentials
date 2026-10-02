# FHIR Verifiable Credentials

A Python tool that turns one HL7 FHIR R4 Immunization record into a signed credential in the W3C Verifiable Credentials shape. Anyone with the issuer's public key can tell whether the credential changed.

**Status: prototype.** 3 tests pass and `ruff check .` is clean on Python 3.9 (October 2026). The walkthrough below was run as written. CI was green on both December 2025 runs.

[![CI](https://github.com/cyber-physical-engineering/fhir-verifiable-credentials/actions/workflows/ci.yml/badge.svg)](https://github.com/cyber-physical-engineering/fhir-verifiable-credentials/actions/workflows/ci.yml)

James Thornton set the architecture and requirements. The code was written with AI-assisted development in late 2025. The tests and checks were re-run in October 2026.

## What it does

- The `fhir-vc` command reads a FHIR Immunization JSON file and writes a credential JSON file.
- The credential carries the W3C VC v2 context, a `urn:uuid` ID, the issuer string you give it, and issuance and expiration dates.
- Its `credentialSubject` holds the patient reference, the vaccine code (CVX preferred), the occurrence date, the lot number and the performers.
- The proof is an Ed25519 signature over the credential without its `proof`, serialized as sorted-key JSON. Signing uses the Python `cryptography` library.
- A small FastAPI app offers `/convert` and `/verify`. Both are demo endpoints; see the limits.
- One adapter exists, for Immunization. Patient and Observation are not built.

## Quick start

```bash
pip install -e .
```

Make an Ed25519 key with the `cryptography` library the install pulled in:

```bash
python -c "from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey; from cryptography.hazmat.primitives import serialization as s; print(Ed25519PrivateKey.generate().private_bytes(s.Encoding.PEM, s.PrivateFormat.PKCS8, s.NoEncryption()).decode())" > issuer.pem
```

With OpenSSL 3 installed, `openssl genpkey -algorithm ed25519 -out issuer.pem` does the same. The `openssl` that ships with macOS (LibreSSL) does not know the algorithm.

Convert the example record:

```bash
fhir-vc examples/input/immunization_example.json \
  --issuer "did:web:hospital.example.com" \
  --key issuer.pem \
  --output immunization_vc.json
```

The output has this structure. Dates, the ID and the signature differ per run.

```json
{
  "@context": ["https://www.w3.org/ns/credentials/v2", "https://w3id.org/security/suites/ed25519-2020/v1"],
  "id": "urn:uuid:...",
  "type": ["VerifiableCredential", "ImmunizationCredential"],
  "issuer": "did:web:hospital.example.com",
  "issuanceDate": "...",
  "credentialSubject": {
    "type": "ImmunizationRecord",
    "patient": {"reference": "...", "display": "..."},
    "vaccineCode": {"system": "http://hl7.org/fhir/sid/cvx", "code": "207", "display": "..."},
    "occurrenceDateTime": "...",
    "lotNumber": "...",
    "performer": [{"function": "...", "actor": "..."}]
  },
  "expirationDate": "...",
  "proof": {
    "type": "Ed25519Signature2020",
    "created": "...",
    "verificationMethod": "did:web:hospital.example.com#key-1",
    "proofPurpose": "assertionMethod",
    "proofValue": "<128 hex characters>"
  }
}
```

Check the proof with the public key:

```python
import json
from cryptography.hazmat.primitives import serialization

vc = json.load(open("immunization_vc.json"))
proof = vc.pop("proof")
key = serialization.load_pem_private_key(open("issuer.pem", "rb").read(), password=None)
key.public_key().verify(bytes.fromhex(proof["proofValue"]), json.dumps(vc, sort_keys=True).encode())
print("signature ok")
```

Change any field and the same call raises `InvalidSignature`.

Run the tests:

```bash
pip install -e ".[dev]"
pytest
```

## The API

```bash
uvicorn fhir_vc.api.main:app
```

`POST /convert` takes `{"fhir": {...}, "issuer_did": "did:web:..."}` and returns a credential signed with a key generated for that request. The key is not kept and the public key is not returned, so nobody can verify that credential later. The endpoint exists to show the shape. `POST /verify` checks that six top-level fields are present and nothing else.

## Limits

- The proof is not a standard proof suite. It signs sorted-key JSON, not a JSON-LD canonical form, and it stores the signature as hex rather than multibase. The `Ed25519Signature2020` label is borrowed.
- The issuer is any string. No DID document is created or resolved.
- `/verify` checks fields, not signatures. Signature checking is shown in the tests and above.
- `/convert` signs with a throwaway key.
- Only Immunization is supported.
- A Dockerfile is included. It was not re-tested in October 2026.
- Nothing here hands a credential to a patient wallet. That is the design goal, not what the code does.

## License

Apache 2.0. See [LICENSE](LICENSE) and [NOTICE](NOTICE).
