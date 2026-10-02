from __future__ import annotations

from fastapi import FastAPI

from .routes.convert import router as convert_router
from .routes.verify import router as verify_router

app = FastAPI(
    title="FHIR Verifiable Credentials",
    version="0.1.0",
    description=(
        "Demo API. /convert signs with a per-request key; "
        "/verify checks required fields only."
    ),
)

app.include_router(convert_router)
app.include_router(verify_router)
