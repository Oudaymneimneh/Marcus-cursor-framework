"""
FLAME Expression Server
Generates facial expressions from audio input.
"""

import logging
import sys
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add parent to path for shared modules
sys.path.insert(0, str(Path(__file__).parent.parent))
from scripts.logging_config import setup_logging

logger = setup_logging("flame")


# ============================================================================
# Models
# ============================================================================


class HealthResponse(BaseModel):
    status: str
    service: str
    timestamp: str
    model_loaded: bool
    gpu_available: bool


class ExpressionRequest(BaseModel):
    audio_base64: str
    sample_rate: int = 16000


class ExpressionResponse(BaseModel):
    blend_shapes: dict[str, float]
    jaw: list[float]
    neck: list[float]
    inference_ms: float


# ============================================================================
# State
# ============================================================================


@dataclass
class ServerState:
    model_loaded: bool = False
    gpu_available: bool = False
    model: Optional[object] = None


state = ServerState()


# ============================================================================
# Lifespan
# ============================================================================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize model on startup"""
    logger.info("Starting FLAME server...")

    # Check GPU
    try:
        import torch
        state.gpu_available = torch.cuda.is_available() or torch.backends.mps.is_available()
        device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
        logger.info(f"Device: {device}")
    except ImportError:
        logger.warning("PyTorch not installed - running in stub mode")
        state.gpu_available = False

    # TODO: Load FLAME model
    # state.model = load_flame_model()
    # state.model_loaded = True
    logger.info("FLAME model: STUB MODE (not loaded)")

    yield

    logger.info("Shutting down FLAME server")


# ============================================================================
# App
# ============================================================================


app = FastAPI(
    title="FLAME Expression Server",
    description="Generates facial blend shapes from audio",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Endpoints
# ============================================================================


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        service="flame-server",
        timestamp=datetime.utcnow().isoformat(),
        model_loaded=state.model_loaded,
        gpu_available=state.gpu_available,
    )


@app.post("/generate", response_model=ExpressionResponse)
async def generate_expression(request: ExpressionRequest):
    """Generate facial expression from audio"""
    t0 = time.perf_counter()

    # Stub response - replace with actual FLAME inference
    blend_shapes = {
        "jawOpen": 0.0,
        "mouthSmile_L": 0.0,
        "mouthSmile_R": 0.0,
        "browInnerUp": 0.0,
        "eyeSquint_L": 0.0,
        "eyeSquint_R": 0.0,
    }

    inference_ms = (time.perf_counter() - t0) * 1000
    logger.info(f"[LATENCY] flame_inference: {inference_ms:.1f}ms")

    return ExpressionResponse(
        blend_shapes=blend_shapes,
        jaw=[0.0, 0.0, 0.0],
        neck=[0.0, 0.0, 0.0],
        inference_ms=inference_ms,
    )


# ============================================================================
# Main
# ============================================================================


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5001)
