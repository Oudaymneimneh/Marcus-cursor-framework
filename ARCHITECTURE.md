# Marcus AI Avatar - Technical Architecture & Development Standards

## Executive Summary

**Current State Assessment**: The project demonstrates solid architectural thinking but suffers from premature optimization. You've built enterprise-grade infrastructure for features that don't yet exist. The backend works, but 60% of planned components are stubs. The code is production-ready in structure but incomplete in implementation.

**Core Issue**: Complexity mismatch - sophisticated multi-service architecture for what's currently a basic chat API with emotional state tracking.

**Recommended Path**: Consolidate, simplify, then expand. Get MVP working flawlessly before adding distributed services.

---

## 1. Design Patterns & Principles

### 1.1 Core Architectural Patterns

**Pattern 1: Layered Architecture (Currently Implemented)**

```mermaid
graph TD
    A[Presentation Layer (API)] --> B[Application Layer (Services)]
    B --> C[Domain Layer (Models, Business Logic)]
    B --> D[Infrastructure Layer (Database, Redis, External APIs)]
```

**Status**: ✅ Well-implemented
**Verdict**: Keep this. It's clean and testable.

**Rules**:
- API layer only handles HTTP concerns (validation, serialization, status codes)
- Services layer orchestrates business logic (`ConversationService`)
- Domain layer contains pure business logic (`PADLogic`, `DialogueGenerator`)
- Infrastructure layer abstracts external dependencies (database, redis, openai)

**Pattern 2: Repository Pattern (Currently Implemented)**

**Status**: ✅ Well-implemented
**Verdict**: Keep this. It decouples business logic from SQLAlchemy.

**Rules**:
- Each model gets its own repository
- Repositories only do CRUD operations
- Business logic stays in services
- No raw SQL in services (goes through repositories)

**Pattern 3: Dependency Injection (Currently Implemented)**

**Status**: ✅ Well-implemented
**Verdict**: Keep this. Makes testing easy.

### 1.2 New Patterns To Add

**Pattern 4: Strategy Pattern for Emotional Logic**

**Problem**: Currently, PAD logic is hardcoded. Need flexibility for different emotional models.
**Solution**: `EmotionalStrategy` abstract base class with `PADStrategy` implementation.

**Pattern 5: Builder Pattern for Prompts**

**Problem**: System prompts are hardcoded strings. Hard to maintain and test.
**Solution**: `PromptBuilder` to construct prompts from templates based on context.

---

## 2. Refactoring Strategy

### Phase 1: Consolidate (Week 1)

**Goal**: Merge distributed stubs into single working service.

**Structure**:
```
src/
├── api/
│   ├── main.py                    # FastAPI app
│   └── routes/
│       ├── chat.py                # Chat endpoints
│       └── admin.py               # Health, metrics
├── domain/
│   ├── models.py                  # SQLAlchemy models
│   ├── repositories.py            # Data access
│   ├── services.py                # Business logic orchestration
│   └── emotional_strategies.py    # NEW: Strategy pattern
├── dialogue/
│   ├── generator.py               # Core dialogue logic
│   ├── prompt_builder.py          # NEW: Builder pattern
│   ├── pad_logic.py               # Emotional calculations
│   └── templates/                 # NEW: Prompt templates
│       ├── system_base.txt
│       ├── guidelines_neutral.txt
│       └── guidelines_melancholic.txt
├── infrastructure/
│   ├── database.py
│   ├── redis.py
│   ├── logging.py
│   ├── metrics.py
│   └── external/                  # NEW: External service clients
│       ├── openai_client.py       # Wrap OpenAI SDK
│       └── future_services.py     # Placeholder for FLAME, TTS
├── config.py
└── __init__.py
```

### Phase 2: Simplify (Week 1-2)

**Goal**: Reduce documentation sprawl and clarify MVP scope.

**MVP Definition**: "Conversational AI with emotional awareness that passes 70% Turing test"

**Core Features (Must Have)**:
- ✓ Chat API that accepts user input
- ✓ LLM-powered response generation
- ✓ PAD emotional state tracking
- ✓ Emotional state influences response tone
- ✓ Conversation history persistence
- ✓ Simple web UI for testing

### Phase 3: Test (Week 2)

**Goal**: Add missing tests.

**Targets**:
- Unit tests: 80%+ coverage on `src/dialogue/` and `src/domain/`
- Integration tests: All API endpoints tested
- E2E tests: At least one happy path through full system

---

## 3. Coding Standards & Rules

### 3.1 Python Standards

- **Line Length**: 88 characters (Ruff default)
- **Target Version**: Python 3.10+
- **Linter**: Ruff (replacing Flake8, Black, isort)

### 3.2 Non-Negotiable Rules

1.  **Type Everything**: All function parameters and return values must have type hints.
2.  **Async Everything**: All I/O operations (DB, API, Redis) must be async.
3.  **Never Leave TODOs**: Raise `NotImplementedError` or link to an issue.
4.  **Log Latency**: Use `@log_latency` decorator for all async operations.
5.  **One Responsibility**: Keep functions short (< 30 lines) and focused.

### 3.3 Anti-Patterns

- ❌ **Premature Optimization**: Don't cache until profiling proves it's needed.
- ❌ **YAGNI Violation**: Don't build features you don't need yet.
- ❌ **Mutable Default Arguments**: `def func(items=[])` is forbidden.
- ❌ **Broad Exceptions**: Catch specific exceptions, not generic `Exception`.
- ❌ **Leaky Abstractions**: Business logic should not know about infrastructure details (e.g., SQL queries in services).

---

## 4. Development Workflow

### 4.1 Feature Development Cycle

1.  **PLAN**: Write ticket, design API/models.
2.  **TEST**: Write failing test first.
3.  **IMPLEMENT**: Minimal code to pass test.
4.  **REFACTOR**: Clean up, extract functions.
5.  **VALIDATE**: Run full suite, commit if green.
6.  **DOCUMENT**: Update docs and changelog.

### 4.2 Git Workflow

- Create feature branch: `feature/emotional-decay`
- Commit often with conventional commits: `feat(dialogue): add emotional decay`
- Squash merge to main.

---

## 5. Decision Log

- **001 Layered Architecture**: Adopting standard layered architecture for separation of concerns.
- **002 Repository Pattern**: Using repositories to abstract database access.
- **003 Emotional Strategy**: Using Strategy pattern for emotional logic to allow future model swapping.


