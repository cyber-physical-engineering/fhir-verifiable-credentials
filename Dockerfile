# FHIR Verifiable Credentials: Docker image for the demo API
# /convert signs with a per-request key; /verify checks required fields only

FROM python:3.11-slim

LABEL org.opencontainers.image.title="fhir-verifiable-credentials"
LABEL org.opencontainers.image.description="Turn a FHIR R4 Immunization record into an Ed25519-signed credential in the W3C Verifiable Credentials shape"

WORKDIR /app

# Copy project files
COPY pyproject.toml README.md ./
COPY fhir_vc ./fhir_vc

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir .

ENV PORT=8080
EXPOSE 8080

# Run the FastAPI server
CMD ["python", "-m", "uvicorn", "fhir_vc.api.main:app", "--host", "0.0.0.0", "--port", "8080"]
