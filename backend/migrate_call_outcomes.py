"""
Migration script to update CallOutcome enum values from old 8-status system to new 4-status system.

OLD VALUES -> NEW VALUES:
- COMPLETED -> BUSY
- IN_PROGRESS -> BUSY
- MEETING_SCHEDULED -> INTERESTED
- FAILED -> NO_ANSWER
- VOICEMAIL -> NO_ANSWER
- DECLINED -> NOT_INTERESTED
- Keep: INTERESTED, NOT_INTERESTED, NO_ANSWER, BUSY
"""
import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.config import get_settings
from backend.database import get_db

settings = get_settings()

def migrate_call_outcomes():
    """Migrate old CallOutcome enum values to new 4-status system"""

    # Create engine
    engine = create_engine(settings.database_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        print("Starting CallOutcome migration...")
        print("-" * 50)

        # Get current counts
        result = session.execute(text("SELECT outcome, COUNT(*) FROM calls WHERE outcome IS NOT NULL GROUP BY outcome"))
        current_counts = dict(result.fetchall())

        print("\nCurrent outcome distribution:")
        for outcome, count in current_counts.items():
            print(f"  {outcome}: {count}")

        print("\n" + "-" * 50)
        print("Applying migrations...\n")

        # Migration mappings
        migrations = [
            ("COMPLETED", "BUSY", "Completed calls without meetings -> Busy"),
            ("IN_PROGRESS", "BUSY", "In-progress calls -> Busy"),
            ("MEETING_SCHEDULED", "INTERESTED", "Meeting scheduled -> Interested"),
            ("FAILED", "NO_ANSWER", "Failed calls -> No Answer"),
            ("VOICEMAIL", "NO_ANSWER", "Voicemail -> No Answer"),
            ("DECLINED", "NOT_INTERESTED", "Declined -> Not Interested"),
        ]

        total_updated = 0

        for old_value, new_value, description in migrations:
            if old_value in current_counts:
                result = session.execute(
                    text("UPDATE calls SET outcome = :new_value WHERE outcome = :old_value"),
                    {"old_value": old_value, "new_value": new_value}
                )
                count = result.rowcount
                total_updated += count
                print(f"[OK] {description}")
                print(f"  Updated {count} records: {old_value} -> {new_value}")

        session.commit()

        print("\n" + "-" * 50)
        print(f"Migration complete! Updated {total_updated} records.")
        print("-" * 50)

        # Get new counts
        result = session.execute(text("SELECT outcome, COUNT(*) FROM calls WHERE outcome IS NOT NULL GROUP BY outcome"))
        new_counts = dict(result.fetchall())

        print("\nNew outcome distribution:")
        for outcome, count in new_counts.items():
            print(f"  {outcome}: {count}")

        print("\n[SUCCESS] Database migration successful!")

    except Exception as e:
        session.rollback()
        print(f"\n[ERROR] Migration failed: {str(e)}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    migrate_call_outcomes()
