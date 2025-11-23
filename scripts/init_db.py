import asyncio
import logging
import sys
from pathlib import Path

# Add project root to python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text
from src.infrastructure.database import get_engine
from src.config import get_settings

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def init_database():
    logger.info("Initializing database...")
    settings = get_settings()
    logger.info(f"Connecting to: {settings.database_url.split('@')[1]}") # Log host only

    engine = get_engine()
    
    # Read schema file
    schema_path = project_root / "sql" / "schema.sql"
    if not schema_path.exists():
        logger.error(f"Schema file not found at {schema_path}")
        return

    with open(schema_path, "r") as f:
        schema_sql = f.read()

    try:
        async with engine.begin() as conn:
            # Split by semicolon to execute statements individually
            # This is a simple split and might break if semicolons are in strings,
            # but for this specific schema file it is safe.
            statements = [s.strip() for s in schema_sql.split(';') if s.strip()]
            
            for statement in statements:
                # Skip empty statements or comments-only
                if not statement:
                    continue
                    
                logger.info(f"Executing: {statement[:50]}...")
                await conn.execute(text(statement))
                
            logger.info("Schema applied successfully.")
            
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(init_database())

