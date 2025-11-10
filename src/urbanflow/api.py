"""FastAPI application for UrbanFlow."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from fastapi import FastAPI, UploadFile

from .logging_utils import get_logger

app = FastAPI(title="UrbanFlow API", version="0.1.0")
logger = get_logger(__name__)


@app.post("/api/v1/optimize")
async def optimize(gtfs_zip: UploadFile, constraints: UploadFile, objective: UploadFile, sample_size: int = 5000, seed: Optional[int] = None) -> dict:
    logger.info("Optimize endpoint not yet implemented")
    return {"status": "not_implemented"}


@app.get("/api/v1/status/{job_id}")
async def status(job_id: str) -> dict:
    logger.info("Status endpoint not yet implemented")
    return {"job_id": job_id, "status": "not_implemented"}
