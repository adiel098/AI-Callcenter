"""
Migration script to add database constraint preventing multiple active calls per lead.

This ensures at the database level that a lead can only have one active call at a time.
"""
import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.config import get_settings

settings = get_settings()

def add_active_call_constraint():
    """Add partial unique index to prevent multiple active calls per lead"""

    engine = create_engine(settings.database_url)

    try:
        print("Adding constraint to prevent duplicate active calls...")
        print("-" * 50)

        with engine.begin() as conn:
            # Check if we're using SQLite
            if 'sqlite' in settings.database_url.lower():
                print("Detected SQLite database")

                # SQLite doesn't support partial indexes with IS NULL in all versions
                # Instead, we'll create a unique index on lead_id where ended_at IS NULL
                # by filtering with a WHERE clause

                # Check if index already exists
                result = conn.execute(text("""
                    SELECT name FROM sqlite_master
                    WHERE type='index' AND name='idx_active_calls_per_lead'
                """))

                if result.fetchone():
                    print("[INFO] Index already exists, skipping")
                    return

                # Create partial unique index (SQLite 3.8.0+)
                conn.execute(text("""
                    CREATE UNIQUE INDEX idx_active_calls_per_lead
                    ON calls(lead_id)
                    WHERE ended_at IS NULL
                """))
                print("[OK] Created unique index on active calls")

            else:
                # For PostgreSQL
                print("Detected PostgreSQL database")

                # Check if index already exists
                result = conn.execute(text("""
                    SELECT indexname FROM pg_indexes
                    WHERE indexname = 'idx_active_calls_per_lead'
                """))

                if result.fetchone():
                    print("[INFO] Index already exists, skipping")
                    return

                # Create partial unique index
                conn.execute(text("""
                    CREATE UNIQUE INDEX idx_active_calls_per_lead
                    ON calls(lead_id)
                    WHERE ended_at IS NULL
                """))
                print("[OK] Created unique index on active calls")

        print("-" * 50)
        print("[SUCCESS] Constraint added successfully!")
        print("\nThis index ensures:")
        print("- Each lead can only have ONE active call (ended_at IS NULL)")
        print("- Multiple completed calls per lead are still allowed")
        print("- Database will reject duplicate active call attempts")

    except Exception as e:
        print(f"\n[ERROR] Migration failed: {str(e)}")
        raise

if __name__ == "__main__":
    add_active_call_constraint()
