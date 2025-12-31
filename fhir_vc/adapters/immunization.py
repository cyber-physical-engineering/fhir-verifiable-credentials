from __future__ import annotations

from typing import Any, cast

from ..core.vc_builder import VCBuilder, VerifiableCredential


class ImmunizationAdapter:
    """Convert FHIR Immunization to a Verifiable Credential."""

    CREDENTIAL_TYPE = "ImmunizationCredential"

    def __init__(self, vc_builder: VCBuilder):
        self.vc_builder = vc_builder

    def convert(self, fhir_immunization: dict[str, Any]) -> VerifiableCredential:
        if fhir_immunization.get("resourceType") != "Immunization":
            raise ValueError("Expected Immunization resource")

        subject = {
            "type": "ImmunizationRecord",
            "patient": self._extract_patient_reference(fhir_immunization),
            "vaccineCode": self._extract_vaccine_code(fhir_immunization),
            "occurrenceDateTime": fhir_immunization.get("occurrenceDateTime"),
            "lotNumber": fhir_immunization.get("lotNumber"),
            "performer": self._extract_performer(fhir_immunization),
        }
        subject = {k: v for k, v in subject.items() if v is not None}

        vc = self.vc_builder.build(subject=subject, credential_type=self.CREDENTIAL_TYPE)
        return self.vc_builder.sign(vc)

    def _extract_patient_reference(self, immunization: dict[str, Any]) -> dict[str, Any]:
        patient = immunization.get("patient", {})
        return {"reference": patient.get("reference"), "display": patient.get("display")}

    def _extract_vaccine_code(self, immunization: dict[str, Any]) -> dict[str, Any]:
        vaccine_code = immunization.get("vaccineCode", {})
        codings = vaccine_code.get("coding", [])

        for coding in codings:
            if "cvx" in str(coding.get("system", "")).lower():
                return {
                    "system": coding.get("system"),
                    "code": coding.get("code"),
                    "display": coding.get("display"),
                }

        if codings:
            return cast(dict[str, Any], codings[0])

        return {"text": vaccine_code.get("text", "Unknown")}

    def _extract_performer(self, immunization: dict[str, Any]) -> list[dict[str, Any]]:
        performers = immunization.get("performer", [])
        return [
            {
                "function": p.get("function", {}).get("text"),
                "actor": p.get("actor", {}).get("display"),
            }
            for p in performers
        ]
