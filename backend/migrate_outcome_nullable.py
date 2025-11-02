"""
Migration script to make Call.outcome nullable in the database.

This allows calls to start without an outcome and have it set during/after the conversation.
"""
import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.config import get_settings

settings = get_settings()

def make_outcome_nullable():
    """Make the outcome column nullable"""

    engine = create_engine(settings.database_url)

    try:
        print("Making Call.outcome column nullable...")
        print("-" * 50)

        with engine.begin() as conn:
            # For SQLite, we need to recreate the table since ALTER COLUMN is not fully supported
            # Check if we're using SQLite
            if 'sqlite' in settings.database_url.lower():
                print("Detected SQLite database - recreating table...")

                # Create backup table
                conn.execute(text("""
                    CREATE TABLE calls_backup AS SELECT * FROM calls
                """))
                print("[OK] Created backup table")

                # Drop original table
                conn.execute(text("DROP TABLE calls"))
                print("[OK] Dropped original table")

                # Recreate table with nullable outcome
                conn.execute(text("""
                    CREATE TABLE calls (
                        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                        lead_id INTEGER NOT NULL,
                        twilio_call_sid VARCHAR(255),
                        recording_url VARCHAR(500),
                        transcript TEXT,
                        summary TEXT,
                        duration FLOAT,
                        language VARCHAR(10),
                        outcome VARCHAR(20),
                        started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        ended_at TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY(lead_id) REFERENCES leads (id)
                    )
                """))
                print("[OK] Created new table with nullable outcome")

                # Copy data back
                conn.execute(text("""
                    INSERT INTO calls (id, lead_id, twilio_call_sid, recording_url, transcript,
                                      summary, duration, language, outcome, started_at, ended_at, created_at)
                    SELECT id, lead_id, twilio_call_sid, recording_url, transcript,
                           summary, duration, language, outcome, started_at, ended_at, created_at
                    FROM calls_backup
                """))
                print("[OK] Copied data back")

                # Drop backup table
                conn.execute(text("DROP TABLE calls_backup"))
                print("[OK] Dropped backup table")

                # Recreate indexes
                conn.execute(text("CREATE INDEX IF NOT EXISTS ix_calls_lead_id ON calls (lead_id)"))
                conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS ix_calls_twilio_call_sid ON calls (twilio_call_sid)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS ix_calls_outcome ON calls (outcome)"))
                print("[OK] Recreated indexes")

            else:
                # For PostgreSQL, we can use ALTER COLUMN
                print("Detected PostgreSQL database - altering column...")
                conn.execute(text("""
                    ALTER TABLE calls ALTER COLUMN outcome DROP NOT NULL
                """))
                print("[OK] Column altered")

        print("-" * 50)
        print("[SUCCESS] Migration complete! Call.outcome is now nullable")

    except Exception as e:
        print(f"\n[ERROR] Migration failed: {str(e)}")
        raise

if __name__ == "__main__":
    make_outcome_nullable()
