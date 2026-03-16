import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import provisions
from app.core.database import init_db

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="Cloud Provisioner",
    description="Enterprise cloud resource provisioning API (LocalStack / AWS)",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    init_db()


@app.get("/health", tags=["health"])
async def health():
    return {"status": "ok"}


app.include_router(provisions.router, prefix="/provisions", tags=["provisions"])
