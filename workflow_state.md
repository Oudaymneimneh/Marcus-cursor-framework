# Marcus AI Avatar - Workflow State

> **Working Memory** - This file tracks current phase, plan, tasks, and session logs.
> Agent: Read this FIRST at start of every session.

---

## State

```yaml
Phase: VALIDATE
Status: COMPLETED
CurrentTask: Frontend Implementation
LastUpdated: 2025-11-23
SessionCount: 2
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
| 2025-11-21 | Use FLAME over Audio2Face | Community feedback: FLAME provides unified lip sync + micro expressions + head movement. Audio2Face only does lip sync. | Audio2Face, custom blend shape system |
| 2025-11-21 | Use Chatterbox over ElevenLabs | Local hosting eliminates API latency, no per-character costs, full voice control | ElevenLabs, Azure TTS, Coqui |
| 2025-11-21 | MetaHuman as base mesh only | Community insight: Keep topology/rig, rebuild textures, reshape face | Full custom model, CC4 |
| 2025-11-21 | Aegis-style .context/ structure | Persistent memory across sessions without MCP dependency | Memory Bank, Graphiti MCP, basic-memory |

