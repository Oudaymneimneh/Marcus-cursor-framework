# Marcus AI Avatar - Technical Architecture

## Executive Summary

**Current State**: Consolidated monolithic backend with emotional awareness and introspection capabilities.

**Architecture**: Layered architecture with clear separation of concerns - API, Service, Domain, Infrastructure.

**MVP Goal**: Conversational AI with emotional awareness that demonstrates human-like interaction patterns.

---

## 1. System Architecture

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Client (Web/Mobile)                   │
└───────────────────────┬─────────────────────────────────┘
                        │ HTTP/REST
                        ▼
┌─────────────────────────────────────────────────────────┐
│                   API Layer (FastAPI)                    │
│  • Request validation (Pydantic)                         │
│  • Response serialization                                │
│  • Dependency injection                                  │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│              Application Layer (Services)                │
│  • ConversationService - orchestrates business logic     │
│  • IntrospectionService - self-awareness & learning      │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│              Domain Layer (Business Logic)               │
│  • DialogueGenerator - core conversation brain           │
│  • PADLogic - emotional state calculations               │
│  • Models - data structures (User, Session, Message)     │
│  • Repositories - data access patterns                   │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│         Infrastructure Layer (External Systems)          │
│  • PostgreSQL - conversation & emotional history         │
│  • Redis - caching & session management                  │
│  • OpenAI - LLM for response generation                  │
│  • Prometheus - metrics & monitoring                     │
└─────────────────────────────────────────────────────────┘
```

### 1.2 Directory Structure

```
src/
├── api/                      # HTTP layer
│   ├── main.py              # FastAPI app & middleware
│   ├── dependencies.py      # Dependency injection
│   └── routes/
│       └── chat.py          # Chat endpoints
│
├── domain/                   # Business logic & models
│   ├── models.py            # SQLAlchemy models (User, Session, Message)
│   ├── repositories.py      # Data access layer
│   ├── services.py          # Business logic orchestration
│   └── introspection.py     # Self-awareness & learning
│
├── dialogue/                 # AI-specific logic
│   ├── generator.py         # Core dialogue brain
│   └── pad_logic.py         # Emotional calculations
│
├── infrastructure/           # External systems
│   ├── database.py          # PostgreSQL connection
│   ├── redis.py             # Redis connection
│   ├── logging.py           # Structured logging
│   ├── metrics.py           # Prometheus metrics
│   └── external/            # External service clients
│       └── llm_client.py    # OpenAI wrapper
│
└── config.py                 # Configuration management
```

---

## 2. Design Patterns

### 2.1 Layered Architecture ✅

**Purpose**: Separation of concerns, testability, maintainability.

**Layers**:
1. **API Layer**: HTTP concerns only (validation, serialization, status codes)
2. **Application Layer**: Orchestrates business logic (ConversationService)
3. **Domain Layer**: Pure business logic (PADLogic, DialogueGenerator)
4. **Infrastructure Layer**: External dependencies (database, Redis, OpenAI)

**Rules**:
- API layer NEVER contains business logic
- Service layer orchestrates, doesn't implement algorithms
- Domain layer knows nothing about HTTP or databases
- Infrastructure layer abstracts external dependencies

**Example**:

```python
# ❌ BAD: Business logic in API route
@router.post("/chat")
async def chat(request: MessageRequest):
    if "sad" in request.content:
        pleasure = -0.5  # DON'T calculate emotions here

# ✅ GOOD: Delegate to service layer
@router.post("/chat")
async def chat(request: MessageRequest, service: ConvService):
    brain = DialogueGenerator(service)
    return await brain.generate_response(...)
```

### 2.2 Repository Pattern ✅

**Purpose**: Abstracts database operations, decouples business logic from persistence.

**Implementation**:

```python
class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_external_id(self, external_id: str) -> Optional[User]:
        stmt = select(User).where(User.external_id == external_id)
        return await self.session.execute(stmt).scalar_one_or_none()
```

**Rules**:
- Each model gets its own repository
- Repositories only do CRUD operations
- Business logic stays in services
- No raw SQL in services

### 2.3 Dependency Injection ✅

**Purpose**: Testability, flexibility, explicit dependencies.

**Implementation**:

```python
# Define dependency
async def get_conversation_service(db: DBSession) -> ConversationService:
    return ConversationService(db)

# Inject via FastAPI
@router.post("/chat")
async def chat(service: ConvService):  # Automatically injected
    ...
```

**Rules**:
- All dependencies injected via `Depends()`
- Easy to override in tests
- No global state or singletons

### 2.4 Strategy Pattern (NEW) ✅

**Purpose**: Swappable algorithms (e.g., different emotional models).

**Implementation**:

```python
class EmotionalStrategy(ABC):
    @abstractmethod
    async def calculate_update(self, current, stimulus) -> Dict[str, float]:
        pass

class PADStrategy(EmotionalStrategy):
    async def calculate_update(self, current, stimulus):
        # PAD implementation
        ...

class ValenceArousalStrategy(EmotionalStrategy):
    async def calculate_update(self, current, stimulus):
        # Simpler 2D model
        ...

# Usage
class DialogueGenerator:
    def __init__(self, service, emotional_strategy: EmotionalStrategy = None):
        self.emotional_strategy = emotional_strategy or PADStrategy()
```

**Why**: Switch emotional models without rewriting DialogueGenerator.

### 2.5 Adapter Pattern (NEW) ✅

**Purpose**: Wrap external services for testability and swappability.

**Implementation**:

```python
class LLMClient(ABC):
    @abstractmethod
    async def generate(self, messages, temperature, max_tokens) -> str:
        pass

class OpenAIClient(LLMClient):
    async def generate(self, messages, temperature, max_tokens) -> str:
        # Real OpenAI API call
        ...

class MockLLMClient(LLMClient):
    async def generate(self, messages, temperature, max_tokens) -> str:
        return "Mock response"  # No API call

# Usage - inject real or mock
generator = DialogueGenerator(service, llm_client=MockLLMClient())  # Testing
generator = DialogueGenerator(service, llm_client=OpenAIClient())   # Production
```

**Why**:
- Testable (no API calls in tests)
- Swappable (easy to add Claude, Gemini, local LLMs)
- Cost control (rate limiting, caching in one place)

---

## 3. Core Components

### 3.1 DialogueGenerator

**Purpose**: Marcus's brain - generates responses with emotional awareness.

**Key Features**:
- Introspection before responding
- Pattern detection
- Strategy selection based on effectiveness data
- Emotional state calculation
- Context-aware prompt construction

**Flow**:

```
User Input
    ↓
1. Save user message to DB
    ↓
2. INTROSPECT: What do I know about this user?
    ↓
3. DETECT PATTERNS: Is this a recurring behavior?
    ↓
4. SELECT STRATEGY: What approach should I use?
    ↓
5. Calculate emotional response (PAD model)
    ↓
6. Build context-aware prompt
    ↓
7. Call LLM (OpenAI)
    ↓
8. MEASURE EFFECTIVENESS: Did it work?
    ↓
9. Save response + behavioral state to DB
    ↓
Return response + metadata
```

### 3.2 PAD Emotional Model

**Purpose**: Track Marcus's emotional state over time.

**Dimensions**:
- **Pleasure**: -1 (displeasure) to +1 (pleasure)
- **Arousal**: -1 (calm) to +1 (excited)
- **Dominance**: -1 (submissive) to +1 (dominant)

**Emotional Quadrants** (based on pleasure + arousal):
- **Exuberant**: High pleasure, high arousal (happy, energetic)
- **Dependent**: High pleasure, low arousal (content, calm)
- **Hostile**: Low pleasure, high arousal (angry, anxious)
- **Bored**: Low pleasure, low arousal (sad, withdrawn)

**Dynamics**:
- **Reactivity**: How strongly emotions respond to stimulus
- **Decay**: Natural return to baseline over time
- **Baseline**: Marcus's default contemplative state

**Example**:

```python
current = {'pleasure': 0.0, 'arousal': 0.0, 'dominance': 0.0}
stimulus = {'pleasure': 0.5, 'arousal': 0.2, 'dominance': 0.0}  # User shared good news

new_state = pad_logic.calculate_update(current, stimulus)
# Result: {'pleasure': 0.1, 'arousal': 0.04, 'dominance': 0.0}
# Quadrant: "Exuberant"
```

### 3.3 Introspection System

**Purpose**: Self-awareness and learning from interactions.

**Capabilities**:
- **Pattern Detection**: Identifies recurring user behaviors
- **Strategy Selection**: Chooses communication approach based on past effectiveness
- **Effectiveness Measurement**: Scores each interaction
- **Relationship Tracking**: Tracks user familiarity (Stranger → Acquaintance → Confidant)

**Example**:

```python
context = await introspection.prepare_response_context(user_id, session_id)
# Returns:
# {
#   "current_emotion": EmotionalState(pleasure=0.1, ...),
#   "patterns": [UserPattern("anxiety_about_work", occurrences=5)],
#   "relationship_stage": "Acquaintance",
#   "emotional_trend": "declining",
#   "warning_flags": ["prolonged_negative_emotion"]
# }

strategy = await introspection.select_strategy(context, user_id)
# Returns: "supportive"  (chosen based on effectiveness data)
```

---

## 4. Data Models

### 4.1 Database Schema

**Users**:
```sql
CREATE TABLE users (
    user_id UUID PRIMARY KEY,
    external_id VARCHAR(255) UNIQUE NOT NULL,
    display_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);
```

**Sessions**:
```sql
CREATE TABLE sessions (
    session_id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(user_id),
    started_at TIMESTAMP DEFAULT NOW(),
    ended_at TIMESTAMP,
    total_turns INTEGER DEFAULT 0
);
```

**Messages**:
```sql
CREATE TABLE messages (
    message_id UUID PRIMARY KEY,
    session_id UUID REFERENCES sessions(session_id),
    role VARCHAR(20) NOT NULL,  -- 'user' or 'assistant'
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**Emotional States**:
```sql
CREATE TABLE emotional_states (
    state_id UUID PRIMARY KEY,
    session_id UUID REFERENCES sessions(session_id),
    message_id UUID REFERENCES messages(message_id),
    pleasure FLOAT NOT NULL,
    arousal FLOAT NOT NULL,
    dominance FLOAT NOT NULL,
    quadrant VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);
```

**Behavioral States**:
```sql
CREATE TABLE behavioral_states (
    behavior_id UUID PRIMARY KEY,
    session_id UUID REFERENCES sessions(session_id),
    relationship_stage VARCHAR(50),
    communication_style VARCHAR(50),
    crisis_level INTEGER,
    flow_data JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 5. Coding Standards

### 5.1 Type Annotations (Mandatory)

```python
# ❌ BAD
def process_message(user_id, content):
    return service.save(user_id, content)

# ✅ GOOD
async def process_message(
    user_id: uuid.UUID,
    content: str
) -> Dict[str, Any]:
    """Process user message and return response."""
    return await service.save(user_id, content)
```

### 5.2 Async Everything (I/O)

```python
# ❌ BAD - Blocking I/O
def get_user(user_id: str) -> User:
    return db.query(User).filter_by(id=user_id).first()

# ✅ GOOD - Async I/O
async def get_user(user_id: uuid.UUID) -> Optional[User]:
    stmt = select(User).where(User.user_id == user_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()
```

### 5.3 Never Leave TODOs

```python
# ❌ BAD
async def calculate_emotional_state(...):
    # TODO: Implement decay logic
    return {'pleasure': 0.0, 'arousal': 0.0, 'dominance': 0.0}

# ✅ GOOD - Either implement or raise NotImplementedError
async def calculate_emotional_state(...):
    raise NotImplementedError(
        "Emotional decay not yet implemented. "
        "Tracked in issue #42."
    )

# ✅ BETTER - Implement with simplified logic, document limitations
async def calculate_emotional_state(...):
    """
    Calculate emotional state with simplified decay.
    
    Note: Current implementation uses linear decay.
    Future: Implement exponential decay with personality-based baselines.
    """
    # Working implementation
    ...
```

### 5.4 Log Latency for All Async Operations

```python
from src.infrastructure.logging import log_latency

@log_latency("database_query")
async def get_user(user_id: uuid.UUID) -> Optional[User]:
    # Automatically logs execution time
    ...

@log_latency("llm_generation")
async def generate_response(messages: List[Dict]) -> str:
    # Automatically logs execution time
    ...
```

### 5.5 One Responsibility per Function

**Guideline**: If a function doesn't fit on your screen, it's too long.
- **Target**: 5-15 lines per function
- **Max**: 30 lines before mandatory refactor

---

## 6. Testing Strategy

### 6.1 Test Structure

```
tests/
├── unit/                    # Fast, isolated tests
│   ├── test_pad_logic.py   # PAD calculations
│   └── test_llm_client.py  # LLM client wrapper
├── integration/             # Tests with real DB (mocked LLM)
│   └── test_chat_flow.py   # End-to-end chat flow
└── e2e/                     # Full system tests (future)
```

### 6.2 Coverage Targets

- **Unit tests**: 80%+ coverage on `src/dialogue/` and `src/domain/`
- **Integration tests**: All API endpoints tested
- **E2E tests**: At least one happy path through full system

### 6.3 Testing with Mocks

```python
# Test with MockLLMClient - no API calls
mock_llm = MockLLMClient(mock_response="Test response")
generator = DialogueGenerator(service, llm_client=mock_llm)

result = await generator.generate_response(user_id, session_id, "Hello")

assert mock_llm.call_count == 1
assert "Test response" in result["response"]
```

---

## 7. Configuration Management

### 7.1 Environment Variables

```bash
# .env file
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/marcus
REDIS_URL=redis://localhost:6379/0
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=500
LOG_LEVEL=INFO
```

### 7.2 Configuration Class

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    redis_url: str
    openai_api_key: str
    openai_model: str = "gpt-4"
    openai_temperature: float = 0.7
    openai_max_tokens: int = 500
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
```

---

## 8. Deployment

### 8.1 Docker Compose

```yaml
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:postgres@db/marcus
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
  
  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=marcus
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
  
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
```

### 8.2 Running Locally

```bash
# Start services
docker-compose up -d

# Run database migrations
docker-compose exec api python scripts/init_db.py

# View logs
docker-compose logs -f api

# Stop services
docker-compose down
```

---

## 9. Monitoring & Observability

### 9.1 Structured Logging

```python
logger.info(
    "[Marcus] Processing message",
    extra={
        "user_id": str(user_id),
        "session_id": str(session_id),
        "message_length": len(user_input)
    }
)
```

### 9.2 Metrics (Prometheus)

**Counters**:
- `marcus_requests_total{method, path, status}`
- `marcus_llm_calls_total{model}`

**Histograms**:
- `marcus_request_duration_seconds{method, path}`
- `marcus_llm_latency_seconds{model}`
- `marcus_db_query_duration_seconds{query_type}`

**Gauges**:
- `marcus_active_sessions`
- `marcus_emotional_state{dimension}` (pleasure, arousal, dominance)

---

## 10. What NOT To Do

❌ **Don't Prematurely Optimize**: Profile first, optimize second.

❌ **Don't Build Features You Don't Need Yet**: YAGNI (You Aren't Gonna Need It).

❌ **Don't Use Mutable Default Arguments**: `def func(items=[])` is a bug waiting to happen.

❌ **Don't Catch Broad Exceptions**: Catch specific exceptions, let others propagate.

❌ **Don't Mix Business Logic with Infrastructure**: Keep them separate.

---

## 11. MVP Scope

### Core Features (Must Have) ✅

- [x] Chat API that accepts user input
- [x] LLM-powered response generation
- [x] PAD emotional state tracking
- [x] Emotional state influences response tone
- [x] Conversation history persistence
- [x] Introspection system (pattern detection, strategy selection)

### Deferred to v2 (Nice to Have) ⏸

- [ ] FLAME facial expressions (wait for visual avatar)
- [ ] TTS voice synthesis (text-only is fine for MVP)
- [ ] Sophisticated prompt engineering (start simple)
- [ ] Multi-model strategy switching (one model is enough)
- [ ] Real-time dashboard (metrics endpoint is enough)

### Acceptance Criteria

- [ ] User can chat via web UI
- [ ] Marcus responds with contextual awareness (references history)
- [ ] Marcus's tone shifts based on emotional state (measurable via sentiment)
- [ ] Conversation history persists across sessions
- [ ] System runs locally with Docker Compose
- [ ] 10 test users complete 5-turn conversations, 70%+ rate responses as "human-like"

---

## 12. Development Workflow

### Feature Development Cycle

1. **PLAN**: Write ticket with acceptance criteria
2. **TEST**: Write failing test for new feature
3. **IMPLEMENT**: Write simplest code to pass test
4. **REFACTOR**: Clean up code, improve naming
5. **VALIDATE**: Run full test suite, manual smoke test
6. **DOCUMENT**: Update docs, add inline comments

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/emotional-decay

# Make changes in small commits
git add src/dialogue/pad_logic.py tests/unit/test_pad_logic.py
git commit -m "feat(dialogue): add emotional decay to PAD logic

- Implemented exponential decay towards baseline
- Added tests for decay behavior
- Refs #42"

# Run tests before pushing
pytest tests/

# Push and create PR
git push origin feature/emotional-decay
```

**Commit message format**:
```
type(scope): short description

- Longer description if needed
- Bullet points for changes
- Refs #issue-number

Types: feat, fix, refactor, test, docs, chore
Scopes: api, dialogue, domain, infrastructure
```

---

## 13. Next Steps

### Immediate (This Week)

- [ ] Run tests: `pytest tests/`
- [ ] Verify Docker setup: `docker-compose up`
- [ ] Load test: 100 concurrent users
- [ ] Fix any linter errors: `ruff check src/`

### Short-Term (Next 2 Weeks)

- [ ] Improve sentiment analysis (use transformer model)
- [ ] Enhance prompt templates (extract to files)
- [ ] Build simple web UI (React/Next.js)
- [ ] E2E testing with real users

### Long-Term (Month 2+)

- [ ] Add FLAME visual expressions (if MVP proves successful)
- [ ] Add TTS voice synthesis
- [ ] Advanced prompt engineering
- [ ] Behavioral pattern learning
- [ ] Multi-model support

---

## 14. References

- **PAD Model**: Mehrabian & Russell (1974) - "An Approach to Environmental Psychology"
- **Design Patterns**: Martin Fowler - "Patterns of Enterprise Application Architecture"
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **SQLAlchemy Async**: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
- **Prometheus Python**: https://github.com/prometheus/client_python

---

**Document Version**: 1.0  
**Last Updated**: 2025-11-26  
**Author**: Marcus AI Team  
**Status**: Active


