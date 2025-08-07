from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings

# Налаштування для PostgreSQL та SQLite
if settings.DATABASE_URL.startswith("postgresql"):
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,  # Перевірка з'єднання перед використанням
        pool_recycle=300,    # Перестворення з'єднань кожні 5 хвилин
        echo=False           # Логування SQL запитів (встановіть True для дебагу)
    )
else:
    # SQLite налаштування
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},  # Потрібно для SQLite
        echo=False,
        json_serializer=lambda obj: obj.isoformat() if hasattr(obj, 'isoformat') else str(obj)
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()