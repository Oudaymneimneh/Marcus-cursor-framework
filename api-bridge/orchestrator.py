"""
API Bridge / Orchestrator
Central coordination layer for Marcus AI Avatar.
"""

import asyncio
import json
import logging
import sys
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add parent to path for shared modules
sys.path.insert(0, str(Path(__file__).parent.parent))
from scripts.logging_config import setup_logging

logger = setup_logging("orchestrator")


# ============================================================================
# Models
# ============================================================================


class HealthResponse(BaseModel):
    status: str
    service: str
    timestamp: str
    services: dict[str, bool]


class UserInput(BaseModel):
    text: str
    timestamp: Optional[str] = None


class AnimationFrame(BaseModel):
    type: str = "animation_frame"
    frame_id: int
    timestamp: str
    blend_shapes: dict[str, float]
    audio_chunk: Optional[str] = None
    pad_state: dict[str, float]


class PADState(BaseModel):
    pleasure: float = 0.0  # -1 to 1
    arousal: float = -0.3  # -1 to 1
    dominance: float = 0.2  # -1 to 1


# ============================================================================
# State
# ============================================================================


@dataclass
class ServerState:
    flame_healthy: bool = False
    tts_healthy: bool = False
    llm_configured: bool = False
    active_connections: int = 0


state = ServerState()

# Marcus emotional states from project_config.md
MARCUS_STATES = {
    "contemplative": PADState(pleasure=0.0, arousal=-0.3, dominance=0.2),
    "teaching": PADState(pleasure=0.3, arousal=0.4, dominance=0.4),
    "stern": PADState(pleasure=-0.2, arousal=0.3, dominance=0.6),
    "warm": PADState(pleasure=0.5, arousal=0.2, dominance=0.3),
    "melancholic": PADState(pleasure=-0.4, arousal=-0.2, dominance=-0.1),
}


# ============================================================================
# Lifespan
# ============================================================================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Check downstream services on startup"""
    logger.info("Starting Orchestrator...")

    # Check downstream services
    await check_services()

    yield

    logger.info("Shutting down Orchestrator")


async def check_services():
    """Check health of downstream services"""
    import httpx

    services = {
        "flame": "http://localhost:5001/health",
        "tts": "http://localhost:5002/health",
    }

    async with httpx.AsyncClient(timeout=5.0) as client:
        for name, url in services.items():
            try:
                response = await client.get(url)
                if response.status_code == 200:
                    setattr(state, f"{name}_healthy", True)
                    logger.info(f"{name} service: healthy")
                else:
                    logger.warning(f"{name} service: unhealthy (status {response.status_code})")
            except Exception as e:
                logger.warning(f"{name} service: unreachable ({e})")


# ============================================================================
# App
# ============================================================================


app = FastAPI(
    title="Marcus AI Avatar Orchestrator",
    description="Central coordination for LLM → TTS → FLAME pipeline",
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
# REST Endpoints
# ============================================================================


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check with downstream service status"""
    return HealthResponse(
        status="healthy",
        service="orchestrator",
        timestamp=datetime.utcnow().isoformat(),
        services={
            "flame": state.flame_healthy,
            "tts": state.tts_healthy,
            "llm": state.llm_configured,
        },
    )


@app.post("/chat")
async def chat(user_input: UserInput):
    """Process user input and return response (non-streaming)"""
    t0 = time.perf_counter()

    # Stub: Replace with actual LLM call
    response_text = f"Marcus contemplates: '{user_input.text}'"

    e2e_ms = (time.perf_counter() - t0) * 1000
    logger.info(f"[LATENCY] chat_e2e: {e2e_ms:.1f}ms")

    return {
        "response": response_text,
        "pad_state": MARCUS_STATES["contemplative"].model_dump(),
        "latency_ms": e2e_ms,
    }


# ============================================================================
# WebSocket Endpoint
# ============================================================================


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time animation streaming"""
    await websocket.accept()
    state.active_connections += 1
    logger.info(f"WebSocket connected (active: {state.active_connections})")

    try:
        while True:
            # Receive user input
            data = await websocket.receive_text()
            message = json.loads(data)

            if message.get("type") == "user_input":
                t0 = time.perf_counter()

                # Process pipeline: LLM → TTS → FLAME
                # Stub: Send mock animation frames
                for frame_id in range(5):
                    frame = AnimationFrame(
                        frame_id=frame_id,
                        timestamp=datetime.utcnow().isoformat(),
                        blend_shapes={"jawOpen": 0.1 * frame_id},
                        pad_state=MARCUS_STATES["contemplative"].model_dump(),
                    )
                    await websocket.send_text(frame.model_dump_json())
                    await asyncio.sleep(0.033)  # ~30fps

                e2e_ms = (time.perf_counter() - t0) * 1000
                logger.info(f"[LATENCY] ws_pipeline_e2e: {e2e_ms:.1f}ms")

    except WebSocketDisconnect:
        state.active_connections -= 1
        logger.info(f"WebSocket disconnected (active: {state.active_connections})")


# ============================================================================
# Main
# ============================================================================


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
