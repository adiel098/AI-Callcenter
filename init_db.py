"""
Initialize database tables for local development
"""
from backend.database import Base, engine

print("Creating database tables...")
try:
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")
    print("\nTables created:")
    for table in Base.metadata.sorted_tables:
        print(f"  - {table.name}")
except Exception as e:
    print(f"❌ Error creating tables: {e}")
    print("\nMake sure:")
    print("  1. PostgreSQL container is running: docker ps")
    print("  2. .env file has correct DATABASE_URL")
    print("  3. DATABASE_URL=postgresql://ai_user:ai_password@localhost:5432/ai_scheduler")
