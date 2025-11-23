"""
FastAPI Dependencies.

Provides dependency injection for routes (Database sessions, Services, Settings).
"""

from typing import AsyncGenerator, Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import get_settings, Settings
from src.infrastructure.database import get_db
from src.domain.services import ConversationService


# Type alias for Database Session
DBSession = Annotated[AsyncSession, Depends(get_db)]


def get_conversation_service(db: DBSession) -> ConversationService:
    """
    Dependency that provides a ConversationService instance.
    
    The service is initialized with the current database session.
    """
    return ConversationService(db)


# Type alias for ConversationService
ConvService = Annotated[ConversationService, Depends(get_conversation_service)]




