"""
Chatterbox TTS Server
Text-to-speech with streaming audio output.
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
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

# Add parent to path for shared modules
sys.path.insert(0, str(Path(__file__).parent.parent))
from scripts.logging_config import setup_logging

logger = setup_logging("tts")


# ============================================================================
# Models
# ============================================================================


class HealthResponse(BaseModel):
    status: str
    service: str
    timestamp: str
    model_loaded: bool
    voice_loaded: bool


class SynthesizeRequest(BaseModel):
    text: str
    voice: str = "marcus"
    speaking_rate: float = 0.9
    pitch: float = -0.1


class SynthesizeResponse(BaseModel):
    audio_base64: str
    duration_ms: float
    ttfb_ms: float


# ============================================================================
# State
# ============================================================================


@dataclass
class ServerState:
    model_loaded: bool = False
    voice_loaded: bool = False
    model: Optional[object] = None


state = ServerState()


# ============================================================================
# Lifespan
# ============================================================================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize TTS on startup"""
    logger.info("Starting Chatterbox TTS server...")

    # TODO: Load Chatterbox model
    # state.model = load_chatterbox()
    # state.model_loaded = True
    logger.info("Chatterbox model: STUB MODE (not loaded)")

    # TODO: Load Marcus voice profile
    # state.voice = load_voice("marcus")
    # state.voice_loaded = True
    logger.info("Voice profile: STUB MODE (not loaded)")

    yield

    logger.info("Shutting down TTS server")


# ============================================================================
# App
# ============================================================================


app = FastAPI(
    title="Chatterbox TTS Server",
    description="Text-to-speech with Marcus voice",
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
        service="tts-chatterbox",
        timestamp=datetime.utcnow().isoformat(),
        model_loaded=state.model_loaded,
        voice_loaded=state.voice_loaded,
    )


@app.post("/synthesize", response_model=SynthesizeResponse)
async def synthesize(request: SynthesizeRequest):
    """Synthesize speech from text"""
    t0 = time.perf_counter()

    # Stub response - replace with actual Chatterbox synthesis
    ttfb_ms = (time.perf_counter() - t0) * 1000

    # Simulate some processing
    import base64
    audio_stub = base64.b64encode(b"RIFF" + b"\x00" * 100).decode()

    duration_ms = (time.perf_counter() - t0) * 1000
    logger.info(f"[LATENCY] tts_ttfb: {ttfb_ms:.1f}ms")
    logger.info(f"[LATENCY] tts_total: {duration_ms:.1f}ms")

    return SynthesizeResponse(
        audio_base64=audio_stub,
        duration_ms=duration_ms,
        ttfb_ms=ttfb_ms,
    )


@app.post("/synthesize/stream")
async def synthesize_stream(request: SynthesizeRequest):
    """Stream synthesized speech"""

    async def audio_generator():
        t0 = time.perf_counter()

        # Stub: yield empty chunks
        # Replace with actual streaming synthesis
        for i in range(5):
            if i == 0:
                ttfb = (time.perf_counter() - t0) * 1000
                logger.info(f"[LATENCY] tts_stream_ttfb: {ttfb:.1f}ms")
            yield b"\x00" * 1024

        total = (time.perf_counter() - t0) * 1000
        logger.info(f"[LATENCY] tts_stream_total: {total:.1f}ms")

    return StreamingResponse(
        audio_generator(),
        media_type="audio/wav",
    )


# ============================================================================
# Main
# ============================================================================


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5002)
