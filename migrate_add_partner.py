"""
Migration script to add partner_id column and partners table
"""
import sqlite3
import sys

# Force UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def migrate_database():
    """Add partner_id column to leads table, create partners table, and add voice columns to calls"""

    conn = sqlite3.connect('ai_scheduler.db')
    cursor = conn.cursor()

    print("Starting database migration...")

    try:
        # Create partners table
        print("1. Creating partners table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS partners (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(255) NOT NULL,
                api_key VARCHAR(64) NOT NULL UNIQUE,
                is_active BOOLEAN NOT NULL DEFAULT 1,
                rate_limit INTEGER NOT NULL DEFAULT 100,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("   ✓ Partners table created")

        # Check if partner_id column exists in leads table
        cursor.execute("PRAGMA table_info(leads)")
        lead_columns = [column[1] for column in cursor.fetchall()]

        if 'partner_id' not in lead_columns:
            print("2. Adding partner_id column to leads table...")
            cursor.execute("""
                ALTER TABLE leads ADD COLUMN partner_id INTEGER REFERENCES partners(id)
            """)
            print("   ✓ Column added")
        else:
            print("2. partner_id column already exists, skipping...")

        # Check if voice columns exist in calls table
        cursor.execute("PRAGMA table_info(calls)")
        call_columns = [column[1] for column in cursor.fetchall()]

        if 'voice_id' not in call_columns:
            print("3. Adding voice_id column to calls table...")
            cursor.execute("""
                ALTER TABLE calls ADD COLUMN voice_id VARCHAR(255)
            """)
            print("   ✓ voice_id column added")
        else:
            print("3. voice_id column already exists, skipping...")

        if 'voice_name' not in call_columns:
            print("4. Adding voice_name column to calls table...")
            cursor.execute("""
                ALTER TABLE calls ADD COLUMN voice_name VARCHAR(255)
            """)
            print("   ✓ voice_name column added")
        else:
            print("4. voice_name column already exists, skipping...")

        # Commit changes
        conn.commit()
        print("\n✓ Migration completed successfully!")

    except Exception as e:
        conn.rollback()
        print(f"\n✗ Migration failed: {str(e)}")
        raise

    finally:
        conn.close()


if __name__ == "__main__":
    migrate_database()
