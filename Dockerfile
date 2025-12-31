# FHIR Verifiable Credentials - Docker Image
# Converts HL7 FHIR resources into W3C Verifiable Credentials

FROM python:3.11-slim

LABEL org.opencontainers.image.title="fhir-verifiable-credentials"
LABEL org.opencontainers.image.description="Convert HL7 FHIR resources into W3C Verifiable Credentials"
LABEL org.opencontainers.image.vendor="Big Data Plumbing"

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
