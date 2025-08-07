from sqlalchemy.orm import Session
from database import get_db
import crud
import schemas
import models

# Test contact creation directly
def test_contact_creation():
    print("Testing contact creation directly...")
    
    # Get database session
    db = next(get_db())
    
    try:
        # Create a test user first
        user_data = schemas.UserCreate(email="debug@example.com", password="testpass123")
        user = crud.create_user(db, user_data)
        print(f"Created user with ID: {user.id}")
        
        # Create a contact
        contact_data = schemas.ContactCreate(
            first_name="Test",
            last_name="User",
            email="test@example.com",
            phone="+380501234567",
            birth_date="1990-01-01",
            additional_data="Test contact"
        )
        
        contact = crud.create_contact(db, contact_data, user.id)
        print(f"Created contact with ID: {contact.id}")
        print(f"Contact user_id: {contact.user_id}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()

if __name__ == "__main__":
    test_contact_creation() 