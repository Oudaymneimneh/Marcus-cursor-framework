# Marcus AI Avatar - Project Configuration

> **Source of Truth** - This file defines project goals, tech stack, constraints, and changelog.
> Last updated: 2025-11-21

---

## Project Identity

**Project Name:** Marcus AI Avatar  
**Codename:** AURELIUS  
**Owner:** Dina  
**Version:** 0.1.0-alpha

---

## Vision & Goals

### Primary Goal
Build an interactive photorealistic Marcus Aurelius avatar that achieves **<2 second end-to-end latency** from user input to animated response, targeting **70%+ Turing test accuracy** for the underlying AI persona.

### Success Metrics
| Metric | Target | Hard Limit |
|--------|--------|------------|
| Total latency | <1600ms | <2800ms |
| LLM response | <800ms | 1200ms |
| TTS first chunk | <400ms | 800ms |
| FLAME inference | <200ms | 400ms |
| Turing test accuracy | 70%+ | 60% minimum |

---

## Tech Stack

### Core Systems
| Component | Technology | Version | Notes |
|-----------|------------|---------|-------|
| Backend | Python | 3.10+ | async/await everywhere |
| Web Framework | FastAPI | 0.100+ | REST + WebSockets |
| TTS | Chatterbox | latest | Local, NOT ElevenLabs |
| Expression System | FLAME | MPI release | NOT Audio2Face |
| 3D Base | MetaHuman | UE5.4+ | Base mesh only, reshape |
| 3D Sculpting | Blender | 4.0+ | Poly Hammer addon |
| Rendering | Unreal Engine | 5.4+ | Real-time |
| Blender Plugin | Poly Hammer DNA | latest | MetaHuman rig in Blender |

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
    "blend_shapes": {"jawOpen": 0.5, ...},
    "audio_chunk": "base64",  # optional
    "pad_state": {"pleasure": 0.0, "arousal": -0.3, "dominance": 0.2}
}

# User input (Client → Server)
{
    "type": "user_input",
    "text": str,
    "timestamp": "ISO8601"
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

### Timeline
- Core Marcus AI: 12-16 weeks
- Visual avatar addition: +8 weeks (parallel)

### Non-Negotiables
- NO ElevenLabs (use Chatterbox)
- NO Audio2Face (use FLAME)
- NO blocking I/O in server code
- NO hardcoded paths
- NO print() for logging
- ALWAYS latency instrumentation
- ALWAYS health check endpoints

---

## Changelog

| Date | Version | Change | Author |
|------|---------|--------|--------|
| 2025-11-21 | 0.1.0 | Initial project setup | Dina |

