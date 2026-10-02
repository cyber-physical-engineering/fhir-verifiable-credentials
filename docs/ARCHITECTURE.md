# Architecture

## Flow

1. Input: one HL7 FHIR R4 JSON resource. Only Immunization has an adapter.
2. Adapter: pulls the fields for the `credentialSubject` (patient reference, vaccine code with CVX preferred, occurrence date, lot number, performers).
3. Envelope: W3C VC v2 fields, a `urn:uuid` ID, issuance date, and expiration at issuance plus `valid_days` (default 365).
4. Proof: Ed25519 over the credential without `proof`, serialized as sorted-key JSON. The signature is stored as hex under the label `Ed25519Signature2020`.

## What a real implementation adds

- JSON-LD canonicalization and a standard proof suite (for example, Data Integrity Proofs).
- DID resolution and key management (a KMS or HSM).
- Signature checking in `/verify`, which today checks only that six fields are present.
