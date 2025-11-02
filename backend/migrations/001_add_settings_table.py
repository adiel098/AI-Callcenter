"""
Database migration: Add settings table and seed with initial system prompt.

Run this script to create the settings table and populate it with the default prompt.

Usage:
    python -m backend.migrations.001_add_settings_table
"""
import sys
import os
from pathlib import Path

# Ensure parent directory is in Python path
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from sqlalchemy import create_engine, text
from backend.config import get_settings
from backend.database import Base, SessionLocal
from backend.models.setting import Setting
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_migration():
    """Run the migration to add settings table"""
    try:
        settings = get_settings()
        engine = create_engine(settings.database_url)

        logger.info("Creating settings table...")

        # Create settings table (will skip if exists)
        Base.metadata.create_all(bind=engine, tables=[Setting.__table__])

        logger.info("✅ Settings table created")

        # Seed with default system prompt from file
        db = SessionLocal()

        # Check if system_prompt_en already exists
        existing = db.query(Setting).filter(Setting.key == "system_prompt_en").first()

        if existing:
            logger.info("⚠️  system_prompt_en already exists in database. Skipping seed.")
        else:
            # Read default prompt from file
            prompts_dir = Path(__file__).parent.parent / "prompts"
            prompt_path = prompts_dir / "system_prompt_en.txt"

            if prompt_path.exists():
                default_prompt = prompt_path.read_text(encoding="utf-8")

                # Create setting
                setting = Setting(
                    key="system_prompt_en",
                    value=default_prompt
                )
                db.add(setting)
                db.commit()

                logger.info("✅ Seeded system_prompt_en with default value from file")
            else:
                logger.warning("⚠️  Default prompt file not found. Skipping seed.")

        db.close()
        logger.info("✅ Migration completed successfully")

    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        raise


def rollback_migration():
    """Rollback the migration (drop settings table)"""
    try:
        settings = get_settings()
        engine = create_engine(settings.database_url)

        logger.info("Rolling back: Dropping settings table...")

        with engine.connect() as conn:
            conn.execute(text("DROP TABLE IF EXISTS settings"))
            conn.commit()

        logger.info("✅ Settings table dropped")

    except Exception as e:
        logger.error(f"❌ Rollback failed: {e}")
        raise


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Settings table migration")
    parser.add_argument(
        "--rollback",
        action="store_true",
        help="Rollback the migration (drop table)"
    )

    args = parser.parse_args()

    if args.rollback:
        confirm = input("Are you sure you want to rollback? This will delete all settings! (yes/no): ")
        if confirm.lower() == "yes":
            rollback_migration()
        else:
            logger.info("Rollback cancelled")
    else:
        run_migration()
