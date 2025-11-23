# Marcus AI Avatar - Cursor Framework

A comprehensive agentic workflow system for developing an interactive photorealistic Marcus Aurelius avatar using Cursor IDE.

---

## Quick Start

1. **Copy this folder** to your project root
2. **Open in Cursor**
3. **Start a new chat** - the agent will read AGENTS.md and greet you

---

## What's Included

```
marcus-cursor-framework/
├── AGENTS.md                 # Session start instructions (Cursor reads this)
├── project_config.md         # Source of truth: goals, stack, constraints
├── workflow_state.md         # Working memory: phase, plan, tasks, log
├── .cursor/
│   └── rules/
│       ├── global.mdc        # Master workflow rules
│       └── python.mdc        # Python-specific standards
└── .context/
    ├── memory/
    │   ├── procedural.md     # HOW to do things
    │   ├── semantic.md       # WHAT things mean
    │   └── episodic.md       # WHAT happened
    └── decisions.md          # Architectural decision log
```

---

## Workflow System

### Phases

| Phase | What Happens | Exit |
|-------|--------------|------|
| **BLUEPRINT** | Planning, drafting | Ask for approval |
| **CONSTRUCT** | Building per plan | Tests pass |
| **VALIDATE** | Final verification | Changelog entry |

### Core Loop

```
PLAN → seek approval → IMPLEMENT → VALIDATE → SUMMARIZE → ITERATE
```

### Error Handling

```
1. ONE fix at a time
2. Test if resolved
3. If not: UNDO, re-analyze
4. Never stack untested fixes
```

---

## Key Principles

| Rule | Why |
|------|-----|
| **Fix cause, not symptom** | Prevents hack-on-hack debt |
| **One fix, test, iterate** | Stops recursive breakage |
| **Don't be helpful, be better** | Quality over speed |
| **Detailed summarization** | Context preservation |
| **Call by name** | Confirms rules are read |

---

## Persistent Memory (.context/)

The framework includes an Aegis-style memory system:

- **procedural.md** - Learned workflows, commands
- **semantic.md** - Definitions, mappings, concepts
- **episodic.md** - Session summaries, what happened
- **decisions.md** - Architectural choices with rationale

This provides context persistence across sessions without MCP dependencies.

---

## Optional: MCP Integration

If you want enhanced memory, add to `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "memory": {
      "command": "npx",
      "args": ["-y", "@anthropics/mcp-memory"]
    }
  }
}
```

The framework works without MCP - the `.context/` files provide similar benefits.

---

## Customization

### Add Project-Specific Rules

Create new `.mdc` files in `.cursor/rules/`:
- `blender.mdc` - Blender Python standards
- `unreal.mdc` - UE5/Blueprint standards
- `frontend.mdc` - If adding web UI

### Add Tech Stack Support

Edit `project_config.md` → ## Tech Stack section

### Change Phases

Edit `workflow_state.md` → ## Plan section

---

## Commands

| Say to Cursor | Result |
|---------------|--------|
| "Continue" | Resume from workflow_state.md |
| "Status" | Report current phase |
| "Plan [feature]" | Enter BLUEPRINT phase |
| "Approve" | Move to CONSTRUCT |
| "Done" | Move to VALIDATE |

---

## Project Usage (Backend)

### 1. Setup Environment
```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your OpenAI API Key and Database URL
```

### 2. Run Backend
```bash
# Start server with hot reload
python3 -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. API Reference

**POST /api/v1/chat**
- **Description:** Send a message to Marcus and get a response + emotional state.
- **Request:**
  ```json
  {
    "content": "Hello Marcus"
  }
  ```
- **Response:**
  ```json
  {
    "response": "Greetings. I am listening.",
    "pad_state": {"pleasure": 0.1, "arousal": 0.0, "dominance": 0.2},
    "mood_label": "Neutral"
  }
  ```

**GET /health**
- **Description:** Check service health.

**GET /docs**
- **Description:** Interactive Swagger UI.

---

## Credits

This framework incorporates patterns from:
- Aegis Framework (persistent memory structure)
- Memory Bank (custom modes pattern)
- Community best practices (error handling, rules)

---

## License

MIT - Use freely for your own projects.

