from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, extract
from datetime import date, timedelta
from typing import List, Optional
import models
import schemas
from utils import get_password_hash
from email_utils import generate_verification_token, send_verification_email

# User operations
def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    hashed_password = get_password_hash(user.password)
    verification_token = generate_verification_token()
    
    db_user = models.User(
        email=user.email, 
        hashed_password=hashed_password,
        is_verified=False,
        verification_token=verification_token
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Send verification email
    send_verification_email(user.email, verification_token)
    
    return db_user

def get_user(db: Session, user_id: int) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.id == user_id).first()

def verify_user_email(db: Session, token: str) -> Optional[models.User]:
    """Verify user email using verification token"""
    user = db.query(models.User).filter(models.User.verification_token == token).first()
    if user:
        user.is_verified = True
        user.verification_token = None
        db.commit()
        db.refresh(user)
    return user

def update_user_avatar(db: Session, user_id: int, avatar_url: str) -> Optional[models.User]:
    """Update user avatar URL"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        user.avatar_url = avatar_url
        db.commit()
        db.refresh(user)
    return user

# Contact operations (user-specific)
def create_contact(db: Session, contact: schemas.ContactCreate, user_id: int) -> models.Contact:
    db_contact = models.Contact(**contact.dict(), user_id=user_id)
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact

def get_contacts(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[models.Contact]:
    return db.query(models.Contact).filter(models.Contact.user_id == user_id).offset(skip).limit(limit).all()

def get_contact(db: Session, contact_id: int, user_id: int) -> Optional[models.Contact]:
    return db.query(models.Contact).filter(
        models.Contact.id == contact_id,
        models.Contact.user_id == user_id
    ).first()

def update_contact(db: Session, contact_id: int, contact: schemas.ContactUpdate, user_id: int) -> Optional[models.Contact]:
    db_contact = db.query(models.Contact).filter(
        models.Contact.id == contact_id,
        models.Contact.user_id == user_id
    ).first()
    if db_contact:
        update_data = contact.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_contact, field, value)
        db.commit()
        db.refresh(db_contact)
    return db_contact

def delete_contact(db: Session, contact_id: int, user_id: int) -> bool:
    db_contact = db.query(models.Contact).filter(
        models.Contact.id == contact_id,
        models.Contact.user_id == user_id
    ).first()
    if db_contact:
        db.delete(db_contact)
        db.commit()
        return True
    return False

def search_contacts(db: Session, query: str, user_id: int) -> List[models.Contact]:
    return db.query(models.Contact).filter(
        and_(
            models.Contact.user_id == user_id,
            or_(
                models.Contact.first_name.ilike(f"%{query}%"),
                models.Contact.last_name.ilike(f"%{query}%"),
                models.Contact.email.ilike(f"%{query}%")
            )
        )
    ).all()

def get_upcoming_birthdays(db: Session, user_id: int, days: int = 7) -> List[models.Contact]:
    today = date.today()
    end_date = today + timedelta(days=days)
    
    current_year_birthdays = db.query(models.Contact).filter(
        and_(
            models.Contact.user_id == user_id,
            extract('month', models.Contact.birth_date) >= today.month,
            extract('day', models.Contact.birth_date) >= today.day,
            extract('month', models.Contact.birth_date) <= end_date.month,
            extract('day', models.Contact.birth_date) <= end_date.day
        )
    ).all()
    
    next_year_birthdays = db.query(models.Contact).filter(
        and_(
            models.Contact.user_id == user_id,
            extract('month', models.Contact.birth_date) >= 1,
            extract('day', models.Contact.birth_date) >= 1,
            extract('month', models.Contact.birth_date) <= end_date.month,
            extract('day', models.Contact.birth_date) <= end_date.day
        )
    ).all()
    
    return current_year_birthdays + next_year_birthdays