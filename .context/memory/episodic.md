# Episodic Memory - WHAT happened

> Session summaries and significant events in project history.
> Update after each significant work session.

---

## Session Log

### Session 1 - 2025-11-21

**Duration:** ~2 hours  
**Phase:** Planning & Setup  
**Outcome:** Project framework established

**Summary:**
- Discussed path selection for visual avatar (Path B → C: simplified MVP toward full interactive)
- Analyzed community insights on MetaHuman development workflows
- Key learnings: FLAME over Audio2Face, Chatterbox over ElevenLabs, MetaHuman as base mesh only
- Created comprehensive 8-phase execution plan
- Designed Cursor rules framework with BLUEPRINT → CONSTRUCT → VALIDATE workflow
- Established .context/ persistent memory structure

**Decisions Made:**
- Latency target: <2000ms E2E
- Expression system: FLAME (not Audio2Face)
- TTS: Chatterbox (local, not ElevenLabs)
- 3D pipeline: MetaHuman → Blender (Poly Hammer) → UE5

**Artifacts Created:**
- `Marcus_Avatar_Execution_Plan.docx`
- `project_config.md`
- `workflow_state.md`
- `.cursor/rules/global.mdc`
- `.cursor/rules/python.mdc`
- `.context/` memory structure

**Next Steps:**
- Await approval for Phase 0: Environment Setup
- Create directory structure
- Configure MCP memory (optional)
- Generate Marcus reference images

---

## Key Events Timeline

| Date | Event | Impact |
|------|-------|--------|
| 2025-11-21 | Project initialized | Framework established |

---

## Lessons Learned

### From Community Research
1. **MetaHuman is a starting point, not a destination** - expect 2+ weeks of customization
2. **Audio2Face is insufficient** - only does lip sync, need FLAME for full expression
3. **Latency of 3.1s is achievable** - community has done it, optimizing to <2s is harder
4. **Uncanny valley priority** - fix micro-expressions before adding features
5. **Expression editor is fragile** - budget time for manual fixes

### From Planning Session
1. **Workflow phases prevent scope creep** - BLUEPRINT → CONSTRUCT → VALIDATE
2. **Single fix rule prevents spiraling** - one fix, test, undo if failed
3. **Persistent memory is essential** - context loss between sessions is costly

---

## Milestones

| Milestone | Target Date | Status | Notes |
|-----------|-------------|--------|-------|
| Project framework | 2025-11-21 | ✅ DONE | |
| Phase 0: Environment | TBD | ⏳ PENDING | Awaiting approval |
| Phase 1: References | TBD | 📋 PLANNED | |
| Phase 2: MetaHuman | TBD | 📋 PLANNED | |
| Phase 3: Blender | TBD | 📋 PLANNED | |
| Phase 4: FLAME | TBD | 📋 PLANNED | |
| Phase 5: TTS | TBD | 📋 PLANNED | |
| Phase 6: Bridge | TBD | 📋 PLANNED | |
| Phase 7: UE5 | TBD | 📋 PLANNED | |
| Phase 8: Optimize | TBD | 📋 PLANNED | |

