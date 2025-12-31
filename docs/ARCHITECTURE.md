# Architecture

## Flow

- Input: HL7 FHIR R4 JSON resource
- Adapter: Resource-type-specific extraction into a `credentialSubject`
- VC envelope: W3C VC v2-compatible fields
- Proof: Demo-grade Ed25519Signature2020-like object (not JSON-LD canonicalized)

## Notes

This repository is designed as a public reference implementation and scaffolding.
For production, add:
- JSON-LD canonicalization
- Standard proof suites (e.g., Data Integrity Proofs)
- DID resolution and key management (KMS/HSM)
