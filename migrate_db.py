from sqlalchemy import create_engine, Column, Boolean, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings
import models

# Create engine
engine = create_engine(settings.DATABASE_URL)

# Create all tables (this will add the new columns)
models.Base.metadata.create_all(bind=engine)

print("Database migration completed successfully!")
print("New columns added:")
print("- users.is_verified (Boolean, default=False)")
print("- users.verification_token (String, nullable=True)")
print("- users.avatar_url (String, nullable=True)") 