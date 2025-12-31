from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


class CryptoSigner:
    """Minimal Ed25519 signer abstraction.

    This is intentionally small: it enables deterministic signing in tests and
    can be swapped for other suites later.
    """

    def sign(self, payload: bytes) -> bytes:  # pragma: no cover
        raise NotImplementedError


@dataclass
class Ed25519Signer(CryptoSigner):
    private_key: Ed25519PrivateKey

    @classmethod
    def generate(cls) -> "Ed25519Signer":
        return cls(private_key=Ed25519PrivateKey.generate())

    @classmethod
    def from_pem(cls, pem_path: str | Path) -> "Ed25519Signer":
        pem_bytes = Path(pem_path).read_bytes()
        key = serialization.load_pem_private_key(pem_bytes, password=None)
        if not isinstance(key, Ed25519PrivateKey):
            raise TypeError("PEM did not contain an Ed25519 private key")
        return cls(private_key=key)

    def sign(self, payload: bytes) -> bytes:
        return self.private_key.sign(payload)
