"""
Migration script to add partner_id column and partners table
"""
import sqlite3
import sys

# Force UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def migrate_database():
    """Add partner_id column to leads table and create partners table"""

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

        # Check if partner_id column exists
        cursor.execute("PRAGMA table_info(leads)")
        columns = [column[1] for column in cursor.fetchall()]

        if 'partner_id' not in columns:
            print("2. Adding partner_id column to leads table...")
            cursor.execute("""
                ALTER TABLE leads ADD COLUMN partner_id INTEGER REFERENCES partners(id)
            """)
            print("   ✓ Column added")
        else:
            print("2. partner_id column already exists, skipping...")

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
