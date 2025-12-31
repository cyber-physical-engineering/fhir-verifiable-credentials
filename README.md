# FHIR Verifiable Credentials

**Transform hospital data into portable, tamper-proof credentials patients own.**

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](pyproject.toml)
[![Docker](https://img.shields.io/badge/docker-ready-green.svg)](Dockerfile)

## The Problem

Healthcare data is trapped. When you get a vaccination, the record lives in a database row you can't access, can't verify, and can't take with you.

## The Solution

This tool converts standard HL7 FHIR resources into **W3C Verifiable Credentials** — cryptographically signed, patient-controlled credentials that can be verified without calling the issuer.

```
┌─────────────────┐      ┌──────────────────────┐      ┌─────────────────┐
│  FHIR Resource  │ ──▶  │  fhir-vc convert     │ ──▶  │  Verifiable     │
│  (Immunization) │      │  --issuer did:web:.. │      │  Credential     │
└─────────────────┘      └──────────────────────┘      └─────────────────┘
```

## Features

- 🏥 **FHIR R4 Native**: Support for Immunization resources (extensible design)
- 🔐 **Ed25519 Signing**: Fast, secure elliptic curve signatures (Ed25519Signature2020)
- 🌐 **DID Support**: `did:web`, `did:key` for issuer identification
- ✅ **Verification Built-in**: Standard W3C VC data model
- 🐳 **Docker Ready**: Production-ready container support

## Quick Start

### CLI Usage

```bash
# Install
pip install -e .

# Generate a test key
python -c "from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey; from cryptography.hazmat.primitives import serialization; key = Ed25519PrivateKey.generate(); print(key.private_bytes(encoding=serialization.Encoding.PEM, format=serialization.PrivateFormat.PKCS8, encryption_algorithm=serialization.NoEncryption()).decode())" > issuer.pem

# Convert a FHIR Immunization to a Verifiable Credential
fhir-vc examples/input/immunization_example.json \
  --issuer "did:web:hospital.example.com" \
  --key issuer.pem \
  --output immunization_vc.json

# View the result
cat immunization_vc.json
```

### Docker Usage

```bash
# Build the image
docker build -t fhir-vc .

# Run the CLI inside Docker
docker run --rm -v $(pwd):/data fhir-vc \
  /data/examples/input/immunization_example.json \
  --issuer "did:web:hospital.example.com" \
  --key /data/issuer.pem \
  --output /data/vc.json
```

### As a Library

```python
import json
from fhir_vc.core.crypto_signer import Ed25519Signer
from fhir_vc.core.vc_builder import VCBuilder
from fhir_vc.adapters.immunization import ImmunizationAdapter
from fhir_vc.core.fhir_parser import parse_fhir_resource

# Load your FHIR resource
with open("examples/input/immunization_example.json") as f:
    data = json.load(f)

# Setup signer and builder
signer = Ed25519Signer.from_pem("issuer.pem")
builder = VCBuilder(issuer_did="did:web:hospital.example.com", signer=signer)

# Convert
adapter = ImmunizationAdapter(builder)
vc = adapter.convert(data)

print(vc.to_json(indent=2))
```

## Supported FHIR Resources

| Resource | Status | Notes |
|----------|--------|-------|
| Immunization | ✅ | Maps vaccine codes, lot numbers, and performers |
| Patient | 🚧 | Planned |
| Observation | 🚧 | Planned |

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/
```

## Related Projects

- [compliance-evidence-locker](../compliance-evidence-locker) - Automated audit evidence
- [sbom-trust-manager](../sbom-trust-manager) - Supply chain security

## License

Apache 2.0 - See [LICENSE](LICENSE)
