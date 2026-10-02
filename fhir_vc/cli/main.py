from __future__ import annotations

import json
from pathlib import Path

import typer

from ..adapters.immunization import ImmunizationAdapter
from ..core.crypto_signer import Ed25519Signer
from ..core.fhir_parser import parse_fhir_resource
from ..core.vc_builder import VCBuilder

app = typer.Typer(
    add_completion=False,
    help="Turn a FHIR Immunization record into a signed Verifiable Credential",
)


@app.command()
def convert(
    input_path: Path = typer.Argument(..., exists=True, readable=True, help="FHIR JSON file"),
    issuer: str = typer.Option(
        ..., "--issuer", help="Issuer DID (e.g., did:web:hospital.example.com)"
    ),
    key: Path = typer.Option(
        ..., "--key", exists=True, readable=True, help="Ed25519 private key PEM"
    ),
    output: Path = typer.Option(Path("vc.json"), "--output", help="Output VC JSON path"),
) -> None:
    """Convert a FHIR resource JSON file into a signed Verifiable Credential."""

    data = json.loads(input_path.read_text())
    resource = parse_fhir_resource(data)

    signer = Ed25519Signer.from_pem(key)
    builder = VCBuilder(issuer_did=issuer, signer=signer)

    if resource.resource_type == "Immunization":
        adapter = ImmunizationAdapter(builder)
        vc = adapter.convert(resource.raw)
    else:
        raise typer.BadParameter(f"Unsupported resourceType: {resource.resource_type}")

    output.write_text(vc.to_json(indent=2))
    typer.echo(str(output))


if __name__ == "__main__":
    app()
