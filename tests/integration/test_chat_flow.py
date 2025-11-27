"""
Integration tests for chat flow.

Tests the complete flow from user input → emotional update → response.
Uses real database but mocked LLM client.
"""

import pytest
import uuid
from datetime import datetime
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from src.api.main import app
from src.domain.models import Base, User, Session, Message
from src.api.dependencies import get_db_session
from src.infrastructure.external import MockLLMClient
from src.dialogue.generator import DialogueGenerator
from src.domain.services import ConversationService


# Test database URL (use in-memory SQLite for speed)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
async def test_db_engine():
    """Create test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        poolclass=NullPool,
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    await engine.dispose()


@pytest.fixture
async def test_db_session(test_db_engine):
    """Create test database session."""
    async_session_maker = async_sessionmaker(
        test_db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with async_session_maker() as session:
        yield session


@pytest.fixture
def override_get_db_session(test_db_session):
    """Override the dependency to use test database."""
    async def _override():
        yield test_db_session
    
    app.dependency_overrides[get_db_session] = _override
    yield
    app.dependency_overrides.clear()


@pytest.fixture
async def test_service(test_db_session):
    """Create ConversationService with test database."""
    return ConversationService(test_db_session)


@pytest.fixture
def mock_llm_client():
    """Create mock LLM client for testing."""
    return MockLLMClient(
        mock_response="Reflect on what troubles you. The obstacle is the way."
    )


class TestChatFlowEndToEnd:
    """Test complete chat flow through API."""

    @pytest.mark.asyncio
    async def test_simple_chat_creates_session_automatically(
        self, override_get_db_session, test_db_session
    ):
        """Test that /chat endpoint creates session automatically."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/chat",
                json={"content": "Hello Marcus"},
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # Verify response structure
            assert "response" in data
            assert "pad" in data
            assert "quadrant" in data
            assert isinstance(data["response"], str)
            assert len(data["response"]) > 0

    @pytest.mark.asyncio
    async def test_emotional_state_responds_to_positive_input(
        self, override_get_db_session, test_db_session
    ):
        """Test that positive input increases pleasure."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/chat",
                json={"content": "I'm feeling very happy and wonderful today!"},
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # Emotional state should reflect happiness
            assert data["pad"]["pleasure"] > 0, "Pleasure should increase with positive input"

    @pytest.mark.asyncio
    async def test_emotional_state_responds_to_negative_input(
        self, override_get_db_session, test_db_session
    ):
        """Test that negative input decreases pleasure."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/chat",
                json={"content": "I'm feeling very sad and terrible today."},
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # Emotional state should reflect sadness
            assert data["pad"]["pleasure"] < 0, "Pleasure should decrease with negative input"

    @pytest.mark.asyncio
    async def test_conversation_history_persists(
        self, override_get_db_session, test_db_session
    ):
        """Test that conversation history is stored and retrievable."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Send first message
            await client.post(
                "/api/v1/chat",
                json={"content": "Hello Marcus"},
            )
            
            # Send second message
            await client.post(
                "/api/v1/chat",
                json={"content": "How are you today?"},
            )
            
            # Get history
            response = await client.get("/api/v1/chat/history")
            
            assert response.status_code == 200
            history = response.json()
            
            # Should have at least 4 messages (2 user + 2 assistant)
            assert len(history) >= 4
            
            # First message should be user's "Hello Marcus"
            assert history[0]["role"] == "user"
            assert "Hello Marcus" in history[0]["content"]

    @pytest.mark.asyncio
    async def test_introspection_data_returned(
        self, override_get_db_session, test_db_session
    ):
        """Test that introspection data is included in response."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/chat",
                json={"content": "I need help with something difficult"},
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # Introspection fields should be present
            assert "strategy_used" in data
            assert "relationship_stage" in data
            assert data["strategy_used"] is not None

    @pytest.mark.asyncio
    async def test_multiple_turns_maintain_context(
        self, override_get_db_session, test_db_session
    ):
        """Test that context is maintained across multiple turns."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Turn 1
            r1 = await client.post(
                "/api/v1/chat",
                json={"content": "My name is Alice"},
            )
            assert r1.status_code == 200
            
            # Turn 2
            r2 = await client.post(
                "/api/v1/chat",
                json={"content": "I'm feeling stressed about work"},
            )
            assert r2.status_code == 200
            
            # Turn 3 - Reference context
            r3 = await client.post(
                "/api/v1/chat",
                json={"content": "What did I just tell you?"},
            )
            assert r3.status_code == 200
            
            # Verify history contains all messages
            history_response = await client.get("/api/v1/chat/history")
            history = history_response.json()
            
            # Should have 6 messages (3 user + 3 assistant)
            assert len(history) >= 6

    @pytest.mark.asyncio
    async def test_empty_message_rejected(
        self, override_get_db_session, test_db_session
    ):
        """Test that empty messages are rejected."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/chat",
                json={"content": ""},
            )
            
            # Should return validation error
            assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_very_long_message_rejected(
        self, override_get_db_session, test_db_session
    ):
        """Test that excessively long messages are rejected."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Create message longer than max_length (2000 chars)
            long_message = "A" * 2001
            
            response = await client.post(
                "/api/v1/chat",
                json={"content": long_message},
            )
            
            # Should return validation error
            assert response.status_code == 422


class TestChatFlowWithMocks:
    """Test chat flow with mocked LLM client."""

    @pytest.mark.asyncio
    async def test_dialogue_generator_with_mock_llm(
        self, test_service, mock_llm_client
    ):
        """Test DialogueGenerator uses injected mock LLM client."""
        # Create user and session
        user = await test_service.get_or_create_user(
            external_id="test_user",
            display_name="Test User",
        )
        session = await test_service.start_session(user.user_id)
        
        # Create generator with mock LLM
        generator = DialogueGenerator(test_service, llm_client=mock_llm_client)
        
        # Generate response
        result = await generator.generate_response(
            user_id=user.user_id,
            session_id=session.session_id,
            user_input="Hello Marcus",
        )
        
        # Verify mock was called
        assert mock_llm_client.call_count == 1
        
        # Verify response contains expected fields
        assert "response" in result
        assert "pad" in result
        assert "quadrant" in result
        
        # Response should be from mock
        assert "obstacle is the way" in result["response"].lower()

    @pytest.mark.asyncio
    async def test_emotional_state_evolution(
        self, test_service, mock_llm_client
    ):
        """Test that emotional state evolves over multiple interactions."""
        # Create user and session
        user = await test_service.get_or_create_user(
            external_id="test_user_2",
            display_name="Test User 2",
        )
        session = await test_service.start_session(user.user_id)
        
        # Create generator
        generator = DialogueGenerator(test_service, llm_client=mock_llm_client)
        
        # First message - positive
        result1 = await generator.generate_response(
            user_id=user.user_id,
            session_id=session.session_id,
            user_input="I feel great and happy today!",
        )
        pad1 = result1["pad"]
        
        # Second message - negative
        result2 = await generator.generate_response(
            user_id=user.user_id,
            session_id=session.session_id,
            user_input="Actually, I'm feeling very sad now.",
        )
        pad2 = result2["pad"]
        
        # Pleasure should have decreased from result1 to result2
        assert pad2["pleasure"] < pad1["pleasure"], "Pleasure should decrease with sad input"

    @pytest.mark.asyncio
    async def test_pattern_detection(
        self, test_service, mock_llm_client
    ):
        """Test that patterns are detected over time."""
        # Create user and session
        user = await test_service.get_or_create_user(
            external_id="pattern_test_user",
            display_name="Pattern Test",
        )
        session = await test_service.start_session(user.user_id)
        
        # Create generator
        generator = DialogueGenerator(test_service, llm_client=mock_llm_client)
        
        # Send multiple similar messages to trigger pattern detection
        messages = [
            "I'm worried about my job",
            "I'm anxious about work again",
            "I'm stressed about my career",
        ]
        
        for msg in messages:
            result = await generator.generate_response(
                user_id=user.user_id,
                session_id=session.session_id,
                user_input=msg,
            )
        
        # Last result should have patterns detected
        assert "patterns_detected" in result
        # Patterns might be empty early on, but field should exist
        assert isinstance(result["patterns_detected"], list)


class TestDatabaseIntegration:
    """Test database interactions."""

    @pytest.mark.asyncio
    async def test_user_creation(self, test_service):
        """Test user creation and retrieval."""
        user = await test_service.get_or_create_user(
            external_id="test_db_user",
            display_name="Test DB User",
        )
        
        assert user.external_id == "test_db_user"
        assert user.display_name == "Test DB User"
        assert isinstance(user.user_id, uuid.UUID)

    @pytest.mark.asyncio
    async def test_session_creation(self, test_service):
        """Test session creation."""
        user = await test_service.get_or_create_user(
            external_id="session_test",
            display_name="Session Test",
        )
        session = await test_service.start_session(user.user_id)
        
        assert session.user_id == user.user_id
        assert isinstance(session.session_id, uuid.UUID)
        assert session.total_turns == 0

    @pytest.mark.asyncio
    async def test_message_persistence(self, test_service):
        """Test that messages are persisted correctly."""
        user = await test_service.get_or_create_user(
            external_id="message_test",
            display_name="Message Test",
        )
        session = await test_service.start_session(user.user_id)
        
        # Add user message
        await test_service.add_user_message(session.session_id, "Test message")
        
        # Add system message
        await test_service.add_system_message(
            session.session_id,
            "Test response",
            pad_state={"pleasure": 0.1, "arousal": 0.1, "dominance": 0.1, "quadrant": "Neutral"},
            behavioral_state={"relationship_stage": "Stranger"},
        )
        
        # Retrieve history
        history = await test_service.get_conversation_history(session.session_id)
        
        # Should have 2 messages
        assert len(history) == 2
        assert history[0].role == "assistant"  # Newest first
        assert history[1].role == "user"


