# Marcus AI Avatar - Execution Roadmap

> **AI-Assisted Development** - What Claude can build now vs. what needs human input.
> Estimated Total: 8-12 focused sessions (not weeks)

---

## Execution Model

```
CLAUDE CAN DO NOW          NEEDS HUMAN INPUT
─────────────────          ─────────────────
• Directory setup          • Blender sculpting
• Python servers           • MetaHuman creation
• Tests & benchmarks       • Visual approvals
• Config files             • Voice sample review
• Documentation            • Turing test execution
• API integrations         • UE5 scene setup
```

---

## Phase 0: Environment Setup

**Time:** ~15 minutes
**Blocker:** None - can start immediately

### Claude Executes
- [x] Create all directory structure
- [ ] Generate requirements.txt for each service
- [ ] Create environment verification script
- [ ] Initialize .context/ memory files
- [ ] Set up logging configuration
- [ ] Create health check endpoints scaffold

### Human Validates
- [ ] Confirm GPU availability (`nvidia-smi`)
- [ ] Install Blender 4.0+ if missing
- [ ] Install Unreal Engine 5.4+ if missing

### Exit
Run `python scripts/verify_environment.py` → all green

---

## Phase 1: Reference & Concept

**Time:** ~30 minutes (Claude) + human review
**Blocker:** None

### Claude Executes
- [ ] Create reference image directory structure
- [ ] Build reference organizer script with tagging
- [ ] Generate style guide template
- [ ] Create image prompt suggestions for AI generation

### Human Provides
- [ ] Collect 10-20 Marcus Aurelius bust photos
- [ ] Generate AI reference images (Midjourney/DALL-E)
- [ ] Approve visual direction

### Exit
`/reference-images/` populated, style guide approved

---

## Phase 2: MetaHuman Base

**Time:** Human-driven (2-4 hours in UE5)
**Blocker:** Requires Unreal Engine

### Claude Executes
- [ ] Document MetaHuman creation steps
- [ ] Create blend shape verification checklist
- [ ] Build FBX export validation script
- [ ] Generate ARKit shape mapping reference

### Human Executes
- [ ] Create MetaHuman in Unreal (elderly male base)
- [ ] Configure age/facial structure
- [ ] Export FBX for Blender

### Exit
`marcus_base.fbx` passes validation script

---

## Phase 3: Blender Sculpting

**Time:** Human-driven (8-20 hours in Blender)
**Blocker:** Requires Poly Hammer, artistic skill

### Claude Executes
- [ ] Create Blender Python utilities
- [ ] Build texture export scripts
- [ ] Generate sculpting reference overlay system
- [ ] Create rig integrity verification script

### Human Executes
- [ ] Import MetaHuman via Poly Hammer
- [ ] Sculpt Marcus likeness
- [ ] Create textures (diffuse, normal, roughness)
- [ ] Add hair/beard grooms
- [ ] Export back to UE5

### Exit
Re-imported MetaHuman animates correctly in UE5

---

## Phase 4: FLAME Server

**Time:** ~2-3 hours (Claude builds, human tests)
**Blocker:** GPU for inference testing

### Claude Executes
- [ ] Scaffold FastAPI server structure
- [ ] Implement FLAME model loader
- [ ] Build audio → expression pipeline
- [ ] Create FLAME → ARKit mapper (50 → 52 shapes)
- [ ] Add latency instrumentation
- [ ] Write unit tests
- [ ] Write latency benchmark tests
- [ ] Create Dockerfile

### Human Validates
- [ ] Verify GPU inference works
- [ ] Confirm <200ms latency target
- [ ] Review expression quality

### Exit
`pytest tests/test_flame.py` passes, latency <200ms

---

## Phase 5: Chatterbox TTS

**Time:** ~2-3 hours (Claude builds, human tunes voice)
**Blocker:** Voice quality is subjective

### Claude Executes
- [ ] Scaffold TTS server
- [ ] Implement streaming audio output
- [ ] Create voice configuration system
- [ ] Build Marcus voice profile template
- [ ] Add latency instrumentation
- [ ] Write unit tests
- [ ] Write TTFB benchmark tests
- [ ] Create Dockerfile

### Human Validates
- [ ] Review voice quality
- [ ] Tune speaking rate, pitch, accent
- [ ] Confirm <400ms TTFB
- [ ] Approve "Marcus sound"

### Exit
`pytest tests/test_tts.py` passes, TTFB <400ms, voice approved

---

## Phase 6: API Bridge & Orchestration

**Time:** ~3-4 hours (Claude builds end-to-end)
**Blocker:** LLM API keys

### Claude Executes
- [ ] Build orchestrator server
- [ ] Implement LLM client (Claude/GPT-4)
- [ ] Create Marcus persona prompt
- [ ] Build pipeline coordinator (LLM → TTS → FLAME)
- [ ] Implement WebSocket streaming
- [ ] Add PAD emotional state tracking
- [ ] Create animation frame protocol
- [ ] Write integration tests
- [ ] Write E2E latency benchmark
- [ ] Create docker-compose.yml for full stack

### Human Provides
- [ ] LLM API keys
- [ ] Approve Marcus persona responses

### Exit
E2E test passes: input → response → animation in <1600ms

---

## Phase 7: Unreal Integration & Validation

**Time:** Human-driven (4-8 hours in UE5) + Claude testing
**Blocker:** Requires UE5, Live Link setup

### Claude Executes
- [ ] Create WebSocket → Live Link bridge docs
- [ ] Build animation data validator
- [ ] Create performance monitoring dashboard
- [ ] Write Turing test protocol
- [ ] Generate test conversation scripts

### Human Executes
- [ ] Import final Marcus into UE5
- [ ] Set up Live Link connection
- [ ] Configure scene (lighting, camera)
- [ ] Optimize for 60fps
- [ ] Run Turing tests with real users

### Exit
60fps rendering, <2s E2E latency, 70%+ Turing accuracy

---

## Quick Reference: What to Ask Claude

| You Want | Say This |
|----------|----------|
| Start Phase 0 | "Set up the environment" |
| Build FLAME server | "Implement the FLAME server" |
| Build TTS server | "Implement the Chatterbox TTS server" |
| Build orchestrator | "Implement the API bridge" |
| Run all tests | "Run the test suite" |
| Check latency | "Run latency benchmarks" |
| Full stack up | "Start all services" |

---

## Realistic Timeline

| Phase | Claude Time | Human Time | Can Parallelize |
|-------|-------------|------------|-----------------|
| 0: Environment | 15 min | 30 min verify | - |
| 1: Reference | 30 min | 2-4 hrs collect | - |
| 2: MetaHuman | 30 min docs | 2-4 hrs create | - |
| 3: Sculpting | 1 hr scripts | 8-20 hrs sculpt | With 4,5,6 |
| 4: FLAME | 2-3 hrs | 1 hr validate | With 3,5 |
| 5: TTS | 2-3 hrs | 2 hrs tune | With 3,4 |
| 6: API Bridge | 3-4 hrs | 1 hr test | With 3 |
| 7: Integration | 2 hrs docs | 4-8 hrs UE5 | After 3,4,5,6 |

**Claude total:** ~12-15 hours of execution
**Human total:** ~20-40 hours (mostly Blender/UE5 work)
**Calendar time:** Can compress to 1-2 weeks if human time is focused

---

## Success Metrics

| Metric | Target | Test Command |
|--------|--------|--------------|
| FLAME latency | <200ms | `pytest tests/test_flame.py::test_latency` |
| TTS TTFB | <400ms | `pytest tests/test_tts.py::test_ttfb` |
| E2E latency | <1600ms | `pytest tests/test_e2e.py::test_latency` |
| Turing accuracy | 70%+ | Manual test protocol |

---

## Budget

| Item | Cost | Notes |
|------|------|-------|
| Visual (Phase 2-3) | $260 | MetaHuman, textures |
| Cloud GPU | $200-400 | If local GPU unavailable |
| LLM API | $100-200 | Claude/GPT-4 calls |
| Contingency | $240 | |
| **Total** | **<$2,000** | |

---

## Now: What's First?

Phase 0 is ready. Say **"Set up the environment"** and I'll:
1. Create all directories
2. Generate requirements.txt files
3. Build verification script
4. Initialize memory system
5. Report what's ready vs. what you need to install

Let's go.
