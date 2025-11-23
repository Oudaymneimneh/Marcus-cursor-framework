# Backend Integration Checklist - Marcus AI

**Current Phase:** API Compatibility Layer for Frontend  
**Goal:** Ensure backend works seamlessly with Antigravity frontend  
**Reference:** `pad-engine.plan.md` (Frontend expects simple `/api/v1/chat` endpoint)

---

## Current Status

### ✅ Completed Infrastructure
- [x] PostgreSQL connected (Supabase)
- [x] Redis connected (local Docker)
- [x] Schema created (`users`, `sessions`, `messages`, `pad_states`)
- [x] Services layer (`ConversationService`)
- [x] Dialogue generator (`DialogueGenerator`)
- [x] PAD emotional logic (`PADLogic`)
- [x] Backend running on port 8000

### ⚠️ API Compatibility Gap

**Current API:**
- `POST /api/v1/sessions` (start session)
- `POST /api/v1/sessions/{session_id}/chat` (chat)

**Frontend Expects:**
- `POST /api/v1/chat` (single endpoint, session implicit)

**Why:** Frontend should be stateless - user doesn't manage sessions manually.

---

## Phase 1: API Compatibility (Next Step - 30 mins)

### 1.1 Add Simplified Chat Endpoint
- [ ] Add `POST /api/v1/chat` endpoint in `src/api/routes/chat.py`
- [ ] Endpoint should:
  - Accept `MessageRequest` (just `content` field)
  - Optionally accept `user_id` or use default guest user
  - Automatically create/reuse session internally
  - Return `ChatResponse` (response + pad_state)

**Implementation:**

```python
@router.post("/chat", response_model=ChatResponse)
async def simple_chat(
    request: MessageRequest,
    service: ConvService
):
    """
    Simplified chat endpoint for frontend.
    Automatically manages sessions internally.
    """
    # Use a default guest user (or extract from auth header later)
    guest_user_id = uuid.UUID('00000000-0000-0000-0000-000000000001')
    
    # Get or create user
    user = await service.get_or_create_user(
        external_id="guest",
        display_name="Guest User"
    )
    
    # Get active session (or create new one)
    # For simplicity: one session per user, reuse if exists
    # In production: sessions should expire/be managed
    # For MVP: just get latest session or create
    sessions = await service.get_user_sessions(user.user_id, limit=1)
    if sessions:
        session_id = sessions[0].session_id
    else:
        session = await service.start_session(user.user_id)
        session_id = session.session_id
    
    # Generate response
    brain = DialogueGenerator(service)
    result = await brain.generate_response(
        user_id=user.user_id,
        session_id=session_id,
        user_input=request.content
    )
    
    return ChatResponse(
        response=result["response"],
        pad_state=result["pad"],
        mood_label=result["quadrant"]
    )
```

### 1.2 Add Missing Service Method
- [ ] Check if `get_user_sessions()` exists in `ConversationService`
- [ ] If not, add it:

```python
async def get_user_sessions(
    self,
    user_id: uuid.UUID,
    limit: int = 10
) -> List[Session]:
    """Get user's recent sessions."""
    result = await self.session_repo.get_user_sessions(user_id, limit)
    return result
```

### 1.3 Test New Endpoint
- [ ] Stop current backend (Ctrl+C in terminal)
- [ ] Restart backend: `python3 -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000`
- [ ] Test with curl:

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"content": "Hello Marcus"}'
```

- [ ] Expected response:

```json
{
  "response": "Hello. How may I assist you?",
  "pad_state": {
    "pleasure": 0.1,
    "arousal": 0.1,
    "dominance": 0.1
  },
  "mood_label": "Neutral"
}
```

---

## Phase 2: CORS Configuration (5 mins)

### 2.1 Update CORS Origins
- [ ] Open `src/config.py`
- [ ] Update line 240-244:

```python
cors_origins_str: str = Field(
    default="http://localhost:3000,http://localhost:3001",  # Added frontend ports
    alias="cors_origins",
    description="Allowed CORS origins (comma-separated).",
)
```

### 2.2 Update .env File
- [ ] Open `project.env` (or create `.env` if missing)
- [ ] Add/update:

```env
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

### 2.3 Verify CORS
- [ ] Restart backend
- [ ] Check startup logs show correct CORS origins
- [ ] From frontend (once created), test no CORS errors in browser console

---

## Phase 3: Response Schema Validation (10 mins)

### 3.1 Verify ChatResponse Schema
- [ ] Current schema in `chat.py`:

```python
class ChatResponse(BaseModel):
    response: str
    pad_state: Dict[str, float]
    mood_label: str
    message_id: Optional[uuid.UUID] = None
```

- [ ] Frontend expects (from `pad-engine.plan.md`):

```typescript
interface Message {
  role: "user" | "assistant";
  content: string;
  timestamp: string;
}
```

**Decision:** Keep backend schema as-is. Frontend will adapt.

**Rationale:** Backend returns rich data (PAD state), frontend can use or ignore it.

### 3.2 Document API Contract
- [ ] Create `docs/API.md` with endpoint documentation:

```markdown
## POST /api/v1/chat

Send a message to Marcus AI.

**Request:**
```json
{
  "content": "Hello Marcus"
}
```

**Response:**
```json
{
  "response": "Hello. How may I assist you?",
  "pad_state": {
    "pleasure": 0.1,
    "arousal": 0.1,
    "dominance": 0.1
  },
  "mood_label": "Neutral",
  "message_id": null
}
```
```

---

## Phase 4: Error Handling (15 mins)

### 4.1 Add Validation
- [ ] Validate message length (1-2000 characters)
- [ ] Update `MessageRequest`:

```python
class MessageRequest(BaseModel):
    content: str = Field(
        ..., 
        min_length=1, 
        max_length=2000,
        description="User message content"
    )
```

### 4.2 Add Rate Limiting (Future)
- [ ] Note: Add rate limiting before production
- [ ] For MVP: Skip (document as TODO)

### 4.3 Test Error Cases
- [ ] Test empty message: `{"content": ""}`
- [ ] Expected: 422 Unprocessable Entity
- [ ] Test too long message: `{"content": "A" * 3000}`
- [ ] Expected: 422 Unprocessable Entity
- [ ] Test missing OpenAI key:
  - [ ] Remove `OPENAI_API_KEY` from env
  - [ ] Restart backend
  - [ ] Expected: Startup error (fail fast)

---

## Phase 5: Health Check Enhancement (10 mins)

### 5.1 Update Health Endpoint
- [ ] Current endpoint: `GET /health`
- [ ] Enhance to return more details:

```python
@app.get("/health")
async def health_check():
    db_healthy = await check_database_health()
    redis_healthy = await check_redis_health()
    
    status = "healthy" if (db_healthy and redis_healthy) else "unhealthy"
    
    return {
        "status": status,
        "services": {
            "database": "up" if db_healthy else "down",
            "redis": "up" if redis_healthy else "down",
            "openai": "configured" if get_settings().openai_api_key else "missing"
        },
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }
```

### 5.2 Test Health Check
- [ ] `curl http://localhost:8000/health`
- [ ] Expected: All services "up"

---

## Phase 6: Logging & Metrics (15 mins)

### 6.1 Add Request Logging
- [ ] Verify `LoggingMiddleware` is active in `main.py`
- [ ] Test: Send chat request, check logs for:
  - Request ID (correlation ID)
  - Latency
  - PAD state changes

### 6.2 Add Metrics
- [ ] Verify Prometheus metrics at `http://localhost:8000/metrics`
- [ ] Should include:
  - `chat_requests_total`
  - `chat_request_duration_seconds`
  - `pad_state_changes_total`

### 6.3 Test Metrics
- [ ] Send 3 chat requests
- [ ] `curl http://localhost:8000/metrics | grep chat`
- [ ] Expected: See counter = 3

---

## Phase 7: Integration Test (20 mins)

### 7.1 Full Flow Test
- [ ] Start fresh backend (clear any state)
- [ ] Send message: "Hello Marcus"
- [ ] Verify response received
- [ ] Send message: "I'm feeling happy today"
- [ ] Verify PAD state changed (pleasure increased)
- [ ] Send message: "What's your name?"
- [ ] Verify Marcus responds with context (remembers conversation)

### 7.2 Emotional State Test
- [ ] Send: "I'm sad"
- [ ] Check PAD state: pleasure < 0
- [ ] Send: "But now I'm better"
- [ ] Check PAD state: pleasure recovered

### 7.3 History Test
- [ ] Send 5 messages
- [ ] Verify last message references earlier context
- [ ] Proves: History retrieval works

---

## Phase 8: Documentation (15 mins)

### 8.1 API Documentation
- [ ] Access Swagger UI: `http://localhost:8000/docs`
- [ ] Verify all endpoints documented
- [ ] Test endpoints directly from Swagger

### 8.2 README Update
- [ ] Update `README.md` with:
  - How to start backend
  - API endpoint overview
  - Environment variables needed

### 8.3 Architecture Diagram
- [ ] Create `docs/ARCHITECTURE.md` with flow diagram:

```
User Input
   ↓
FastAPI (/api/v1/chat)
   ↓
DialogueGenerator
   ├→ ConversationService (get history)
   ├→ PADLogic (calculate emotion)
   ├→ OpenAI (generate response)
   └→ ConversationService (save response + state)
   ↓
Response (text + PAD)
```

---

## Phase 9: Deployment Prep (Future)

### 9.1 Environment Variables Audit
- [ ] List all required env vars
- [ ] Create `.env.production.example`
- [ ] Document secrets management strategy

### 9.2 Database Migrations
- [ ] Verify Alembic is configured
- [ ] Test migration: `alembic upgrade head`
- [ ] Document migration process

### 9.3 Container Build
- [ ] Test Docker build: `docker build -t marcus-api .`
- [ ] Test container run
- [ ] Document docker-compose usage

---

## Quality Gates (Before Declaring "Backend Complete")

### Code Quality
- [ ] No linter errors: `ruff check src/`
- [ ] Type hints on all functions
- [ ] Docstrings on all public methods
- [ ] No TODOs in critical paths

### Performance
- [ ] Chat endpoint latency < 2 seconds (p95)
- [ ] Database connection pooling working
- [ ] Redis caching functional

### Reliability
- [ ] 10 consecutive chat requests succeed
- [ ] Restart backend, state persists (history intact)
- [ ] Disconnect database, graceful error handling

### Security
- [ ] No API keys in code
- [ ] CORS restricted (not "*")
- [ ] Input validation on all endpoints

---

## Next Immediate Steps (Start Here)

**Priority 1: API Compatibility** (Do This First)
1. Add `POST /api/v1/chat` endpoint
2. Test with curl
3. Verify CORS configuration

**Priority 2: Integration Test**
1. Run full flow test (7.1)
2. Verify emotional state tracking (7.2)

**Priority 3: Documentation**
1. Update README
2. Test Swagger docs

**Estimated Time:** 1.5 hours to complete all critical items.

---

## Notes

**DO:**
- Keep backend simple (MVP mindset)
- Test after every change
- Document as you go

**DON'T:**
- Add features not needed by frontend
- Skip error handling
- Hardcode values

**Current Blocker:** None! Backend is functional, just needs compatibility layer.

**Ready to Execute:** Say "Add chat endpoint" and I'll implement it.



