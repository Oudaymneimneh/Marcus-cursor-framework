import asyncio
import logging
import sys
from pathlib import Path
from sqlalchemy import text

# Add project root to python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.infrastructure.database import get_engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def reset_database():
    logger.info("⚠️  DESTRUCTIVE: Dropping all tables...")
    engine = get_engine()
    
    async with engine.begin() as conn:
        # Drop all known tables with CASCADE
        tables = [
            "events", "strategies", "patterns", "behavioral_states", 
            "pad_states", "messages", "sessions", "users"
        ]
        for table in tables:
            logger.info(f"Dropping {table}...")
            await conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE;"))
            
    logger.info("✅ All tables dropped.")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(reset_database())
