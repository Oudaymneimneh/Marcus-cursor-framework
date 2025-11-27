# Marcus AI Avatar - Workflow State

> **Working Memory** - This file tracks current phase, plan, tasks, and session logs.
> Agent: Read this FIRST at start of every session.

---

## State

```yaml
Phase: CONSTRUCT
Status: INTROSPECTION_ENHANCED
CurrentTask: Marcus Brain Enhancement Complete - Ready for Testing
LastUpdated: 2025-11-27
SessionCount: 4
```

---

## Plan

### Phase 0: Environment Setup (PENDING APPROVAL)

**Objective:** Establish project structure, verify tools, configure MCP memory.

**Steps:**
1. [ ] Create directory structure per project_config.md
2. [ ] Generate requirements.txt for each service
3. [ ] Create environment verification script
4. [ ] Configure .cursor/mcp.json for persistent memory
5. [ ] Set up .context/ memory structure (Aegis pattern)
6. [ ] Verify: Python 3.10+, Blender 4.0+, Node.js 18+, GPU availability
7. [ ] Output: setup_report.md with pass/fail for each component

**Estimated Duration:** 2-4 hours

**Dependencies:** None

**Risks:**
- GPU not available → Will need cloud setup
- Blender not installed → Manual install required

**Exit Criteria:**
- [ ] All directories exist
- [ ] Verification script passes
- [ ] MCP memory server responding
- [ ] .context/ structure initialized

---

## Rules

### Workflow Rules
```
RULE_PHASE_GATE: Cannot enter CONSTRUCT without NEEDS_PLAN_APPROVAL → APPROVED
RULE_SINGLE_FIX: On error, attempt ONE fix, validate, undo if failed, re-analyze
RULE_ROOT_CAUSE: Fix problems at the cause, not the symptom
RULE_NO_PLACEHOLDERS: Never leave TODOs, stubs, or incomplete code
RULE_LATENCY_LOG: All server code must include latency instrumentation
RULE_VALIDATION: Run tests after every atomic change
```

### Automatic Rules
```
RULE_LOG_ROTATE_01: 
  Trigger: length(## Log) > 5000 chars
  Action: Summarize top 5 points to ## ArchiveLog, clear ## Log

RULE_SUMMARY_01:
  Trigger: Phase == VALIDATE && Status == COMPLETED
  Action: Append one-sentence dated entry to project_config.md ## Changelog

RULE_SESSION_START:
  Trigger: New conversation
  Action: Read workflow_state.md → Read project_config.md → Greet by name
```

---

## Items

### Backlog
| ID | Priority | Description | Dependencies |
|----|----------|-------------|--------------|
| ENV-001 | P0 | Create directory structure | None |
| ENV-002 | P0 | Setup verification script | ENV-001 |
| ENV-003 | P0 | Configure MCP memory | ENV-001 |
| REF-001 | P1 | Generate Marcus reference images | ENV-001 |
| REF-002 | P1 | Create reference organizer script | REF-001 |
| MH-001 | P2 | Create MetaHuman base | REF-001 |
| MH-002 | P2 | Export FBX verification | MH-001 |
| BL-001 | P2 | Blender sculpting setup | MH-002 |

### Active
*None - awaiting plan approval*

### Blocked
*None*

### Completed
*None*

---

## Log

```
[2025-11-27 SESSION_4] INTROSPECTION_ENHANCEMENT
- Enhanced strategy selection with keyword-based crisis/energy detection
  * Added 16 crisis keywords, 16 energy keywords
  * PAD-based crisis threshold lowered to -0.5
  * PAD-based energy threshold set to -0.3
  * Pattern-based strategy selection (catastrophizing → reflective)
- Verified advanced sentiment analyzer integration
  * Added transformers, torch to requirements.txt
  * Improved logging to show which mode is active
- Enhanced pattern detection with false positive prevention
  * Expanded catastrophizing keywords (20 total)
  * Expanded solution-seeking keywords (20 total)
  * Added balance indicators for false positive prevention
  * Multi-indicator confidence scoring
- Calibrated effectiveness formula
  * Adjusted pleasure weight from 3.0 to 2.5
  * Added arousal contribution for both high and low states
  * Added strategy-appropriate bonus (+0.2 for correct strategy)
  * Enhanced negative streak break detection
- Added learning tracking system
  * get_learning_metrics() - tracks learning stage
  * calculate_learning_curve() - measures improvement over time
  * Learning stages: cold_start → warming_up → learning → proficient → expert
- Status: Ready for testing with 50+ scenarios
- Time: ~2 hours

[2025-11-26 SESSION_3 - Part 2] API_COMPATIBILITY_LAYER
- Verified simplified /api/v1/chat endpoint (already implemented!)
- Enhanced health check with M4 Max hardware info
- Verified CORS configuration includes frontend ports
- Created comprehensive API_TESTING_GUIDE.md
- All backend compatibility tasks complete
- Status: Ready for frontend integration
- Time: ~30 minutes

[2025-11-26 SESSION_3 - Part 1] HARDWARE_UPGRADE
- Detected Apple M4 Max (40-core GPU, 64GB RAM)
- Updated project_config.md with enhanced targets:
  * Latency: <800ms (from <2000ms)
  * Quality: 4K@60fps, 48kHz audio, 50K particles
  * Models: Full precision (no quantization)
- Updated FLAME server for Metal GPU acceleration
- Updated TTS server for 48kHz studio audio
- Created M4_MAX_CONFIG.md with comprehensive settings
- Decision logged: Leverage local GPU, eliminate cloud costs
- Status: Configuration complete, ready to proceed

[2025-11-21 15:00:00] SESSION_START
- Initialized project_config.md
- Initialized workflow_state.md
- Phase: BLUEPRINT
- Status: NEEDS_PLAN_APPROVAL
- Awaiting Dina's approval to proceed with Phase 0: Environment Setup

[2025-11-21 15:00:01] PLAN_CREATED
- Created Phase 0 plan with 7 steps
- Exit criteria defined
- Risk assessment complete
```

---

## ArchiveLog

*Empty - no rotations yet*

---

## Decisions

| Date | Decision | Rationale | Alternatives Considered |
|------|----------|-----------|------------------------|
| 2025-11-26 | Upgrade targets for M4 Max hardware | Development machine upgraded to M4 Max (40-core GPU, 64GB RAM). Reconfigured all quality targets: 4K@60fps, 48kHz audio, <800ms latency, 50K particles, full-precision models. Local GPU eliminates cloud costs. | Keep conservative targets, cloud GPU offload |
| 2025-11-21 | Use FLAME over Audio2Face | Community feedback: FLAME provides unified lip sync + micro expressions + head movement. Audio2Face only does lip sync. | Audio2Face, custom blend shape system |
| 2025-11-21 | Use Chatterbox over ElevenLabs | Local hosting eliminates API latency, no per-character costs, full voice control | ElevenLabs, Azure TTS, Coqui |
| 2025-11-21 | MetaHuman as base mesh only | Community insight: Keep topology/rig, rebuild textures, reshape face | Full custom model, CC4 |
| 2025-11-21 | Aegis-style .context/ structure | Persistent memory across sessions without MCP dependency | Memory Bank, Graphiti MCP, basic-memory |

