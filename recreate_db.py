from sqlalchemy import text
from database import engine, SessionLocal
import models
from config import settings

def recreate_database():
    print("Recreating database tables...")
    print(f"Using database: {settings.DATABASE_URL}")
    
    # Create a session
    db = SessionLocal()
    
    try:
        # Drop all tables
        print("Dropping existing tables...")
        models.Base.metadata.drop_all(bind=engine)
        print("✅ Tables dropped successfully")
        
        # Create all tables with new schema
        print("Creating new tables...")
        models.Base.metadata.create_all(bind=engine)
        print("✅ Tables created successfully")
        
        # Verify tables were created
        if settings.DATABASE_URL.startswith("sqlite"):
            result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            tables = [row[0] for row in result]
            print(f"Created tables: {tables}")
            
            # Check contacts table structure
            result = db.execute(text("PRAGMA table_info(contacts)"))
            columns = [row[1] for row in result]
            print(f"Contacts table columns: {columns}")
        else:
            # PostgreSQL
            result = db.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'"))
            tables = [row[0] for row in result]
            print(f"Created tables: {tables}")
            
            # Check contacts table structure
            result = db.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'contacts'"))
            columns = [row[0] for row in result]
            print(f"Contacts table columns: {columns}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()

if __name__ == "__main__":
    recreate_database() 