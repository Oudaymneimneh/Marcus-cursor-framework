# Marcus AI Avatar - Project Configuration

> **Source of Truth** - This file defines project goals, tech stack, constraints, and changelog.
> Last updated: 2025-11-26

---

## Project Identity

**Project Name:** Marcus AI Avatar  
**Codename:** AURELIUS  
**Owner:** Dina  
**Version:** 0.2.0-alpha

---

## Hardware Profile

**Development Machine:** Apple M4 Max (2024)
- **CPU:** 16 cores (12 performance + 4 efficiency)
- **GPU:** 40 cores (Metal-accelerated)
- **RAM:** 64 GB unified memory
- **Storage:** 926 GB SSD (721 GB available)
- **Acceleration:** Metal Performance Shaders (MPS) native support

**Capabilities Unlocked:**
- Parallel processing (LLM + TTS + FLAME simultaneously)
- High-resolution models without quantization
- 4K rendering @ 60fps
- Real-time GPU inference across all services
- 128K token context windows
- Studio-quality audio generation (48kHz)

---

## Vision & Goals

### Primary Goal
Build an interactive photorealistic Marcus Aurelius avatar that achieves **<800ms end-to-end latency** from user input to animated response, targeting **70%+ Turing test accuracy** for the underlying AI persona.

### Success Metrics (M4 Max Optimized)
| Metric | Target | Stretch Goal | Notes |
|--------|--------|--------------|-------|
| Total latency | <800ms | <500ms | Parallel pipeline |
| LLM response | <400ms | <250ms | Metal acceleration |
| TTS first chunk | <150ms | <100ms | GPU inference |
| FLAME inference | <50ms | <30ms | Metal MPS |
| Frame rate | 60fps | 120fps | High refresh displays |
| Render quality | 4K | 4K HDR | Native resolution |
| Particle count | 50,000 | 100,000 | Advanced shaders |
| Turing test accuracy | 70%+ | 80%+ | Enhanced context |

---

## Tech Stack

### Core Systems
| Component | Technology | Version | Notes |
|-----------|------------|---------|-------|
| Backend | Python | 3.10+ | async/await, Metal MPS support |
| Web Framework | FastAPI | 0.100+ | REST + WebSockets |
| TTS | Chatterbox | latest | 48kHz studio quality, GPU-accelerated |
| Expression System | FLAME | MPI release | 1024x1024 resolution, Metal optimized |
| 3D Base | MetaHuman | UE5.4+ | 4K textures, high-poly mesh |
| 3D Sculpting | Blender | 4.0+ | Poly Hammer addon, full detail |
| Rendering | Unreal Engine | 5.4+ | 4K @ 60fps, ray-tracing enabled |
| Blender Plugin | Poly Hammer DNA | latest | MetaHuman rig in Blender |
| GPU Framework | Metal | latest | Native Apple Silicon acceleration |

### Communication
| Protocol | Use Case |
|----------|----------|
| WebSockets | Real-time animation streaming |
| REST | Configuration, health checks |
| gRPC | Optional high-performance internal |

### Data Formats
```python
# Animation frame (Server → Client)
{
    "type": "animation_frame",
    "frame_id": int,
    "timestamp": "ISO8601",
    "blend_shapes": {"jawOpen": 0.5, ...},  # 52+ blend shapes at 60fps
    "audio_chunk": "base64",  # 48kHz, 24-bit
    "pad_state": {"pleasure": 0.0, "arousal": -0.3, "dominance": 0.2},
    "quality_metrics": {"fps": 60, "latency_ms": 15}
}

# User input (Client → Server)
{
    "type": "user_input",
    "text": str,
    "timestamp": "ISO8601"
}
```

### Quality Settings (M4 Max)
```python
QUALITY_CONFIG = {
    "audio": {
        "sample_rate": 48000,  # 48kHz studio quality
        "bit_depth": 24,
        "channels": 1,  # mono
        "format": "pcm_s24le"
    },
    "expressions": {
        "resolution": 1024,  # 1024x1024 blend shape maps
        "fps": 60,
        "blend_shape_count": 52,  # ARKit standard
        "smoothing_window": 5  # frames
    },
    "rendering": {
        "target_resolution": [3840, 2160],  # 4K
        "target_fps": 60,
        "particle_count": 50000,
        "shader_quality": "ultra",
        "post_processing": True
    },
    "llm": {
        "context_window": 32000,  # 32K tokens (can go to 128K)
        "temperature": 0.7,
        "top_p": 0.9
    }
}
```

---

## Critical Patterns & Conventions

### Code Style
- **Python**: Black formatter, 88 char lines, type hints mandatory
- **Naming**: snake_case functions, PascalCase classes, SCREAMING_SNAKE constants
- **Imports**: stdlib → third-party → local, alphabetized within groups
- **Async**: All I/O operations must be async

### Latency Instrumentation (MANDATORY)
Every server component MUST include timing:
```python
import time
import logging
logger = logging.getLogger(__name__)

def log_latency(stage: str):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            t0 = time.perf_counter()
            result = await func(*args, **kwargs)
            ms = (time.perf_counter() - t0) * 1000
            logger.info(f"[LATENCY] {stage}: {ms:.1f}ms")
            return result
        return wrapper
    return decorator
```

### Error Handling Pattern
```python
async def process_with_fallback(data):
    try:
        return await primary_processor(data)
    except PrimaryError as e:
        logger.warning(f"Primary failed: {e}")
        return await fallback_processor(data)
    except Exception as e:
        logger.error(f"All failed: {e}")
        return default_neutral_state()
```

### PAD Emotional Framework
```python
@dataclass
class PADState:
    pleasure: float   # -1 to 1
    arousal: float    # -1 to 1
    dominance: float  # -1 to 1

MARCUS_STATES = {
    "contemplative": PADState(0.0, -0.3, 0.2),
    "teaching": PADState(0.3, 0.4, 0.4),
    "stern": PADState(-0.2, 0.3, 0.6),
    "warm": PADState(0.5, 0.2, 0.3),
    "melancholic": PADState(-0.4, -0.2, -0.1),
}
```

---

## Directory Structure

```
/marcus-avatar
├── .context/                    # Aegis-style persistent memory
│   ├── memory/
│   │   ├── procedural.md       # How to do things
│   │   ├── semantic.md         # What things mean
│   │   └── episodic.md         # What happened
│   ├── tasks/
│   │   ├── backlog.md
│   │   ├── active.md
│   │   └── completed.md
│   └── decisions.md            # Decision log with rationale
├── .cursor/
│   ├── rules/                  # Cursor rules
│   │   ├── global.mdc
│   │   ├── python.mdc
│   │   └── avatar.mdc
│   └── mcp.json               # MCP server config
├── project_config.md          # THIS FILE
├── workflow_state.md          # Current workflow state
├── /flame-server
├── /tts-chatterbox
├── /api-bridge
├── /unreal-project
├── /blender-projects
├── /reference-images
├── /docs
└── /tests
```

---

## Constraints

### Budget
- Total: $2,000
- Visual avatar: $260 allocated
- Remaining: $1,740 for infrastructure/APIs
- **Note:** Local hardware eliminates cloud GPU costs

### Timeline (Accelerated with M4 Max)
- Core Marcus AI: 8-12 weeks (reduced from 12-16)
- Visual avatar addition: +6 weeks parallel (reduced from 8)
- **Total:** 14-18 weeks (vs original 20-24 weeks)

### Hardware Requirements
- **Development:** Apple M4 Max or equivalent
- **Minimum Deployment:** M1 Max / RTX 3080 or better
- **Recommended Deployment:** M3 Max+ / RTX 4080+
- **RAM:** 32GB minimum, 64GB recommended
- **Storage:** 500GB SSD minimum for models/assets

### Non-Negotiables
- NO ElevenLabs (use Chatterbox)
- NO Audio2Face (use FLAME)
- NO blocking I/O in server code
- NO hardcoded paths
- NO print() for logging
- NO model quantization (use full precision with M4 Max)
- ALWAYS latency instrumentation
- ALWAYS health check endpoints
- ALWAYS Metal GPU acceleration where available

---

## Changelog

| Date | Version | Change | Author |
|------|---------|--------|--------|
| 2025-11-26 | 0.2.0 | Hardware upgrade to M4 Max - reconfigured all quality/performance targets for high-end GPU acceleration | Dina |
| 2025-11-21 | 0.1.0 | Initial project setup | Dina |

