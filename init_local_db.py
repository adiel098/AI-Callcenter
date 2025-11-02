"""
Initialize local database tables
This script uses the local PostgreSQL container directly
"""
import os
os.environ['DATABASE_URL'] = 'postgresql://ai_user:ai_password@localhost:5432/ai_scheduler'

from backend.database import Base
from sqlalchemy import create_engine

# Create engine with local DATABASE_URL
engine = create_engine('postgresql://ai_user:ai_password@localhost:5432/ai_scheduler')

print("Creating database tables with local PostgreSQL...")
print("DATABASE_URL: postgresql://ai_user:ai_password@localhost:5432/ai_scheduler")
print()

try:
    Base.metadata.create_all(bind=engine)
    print("SUCCESS! Database tables created!")
    print()
    print("Tables created:")
    for table in Base.metadata.sorted_tables:
        print(f"  - {table.name}")
    print()
    print("You can now start the services:")
    print("  Terminal 1: py -3.13 -m uvicorn backend.main:app --reload")
    print("  Terminal 2: py -3.13 -m celery -A backend.workers.celery_app worker --loglevel=info --pool=solo")
    print("  Terminal 3: cd frontend && npm run dev")
except Exception as e:
    print(f"ERROR creating tables: {e}")
    print()
    print("Troubleshooting:")
    print("  1. Make sure PostgreSQL container is running:")
    print("     docker ps | findstr homework-postgres")
    print()
    print("  2. If not running, start it:")
    print("     docker start homework-postgres")
    print()
    print("  3. Verify connection:")
    print("     docker exec homework-postgres psql -U ai_user -d ai_scheduler -c 'SELECT 1'")
