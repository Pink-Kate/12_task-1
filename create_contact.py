#!/usr/bin/env python3
"""
Створення контакту з правильним кодуванням
"""
import requests
import json

def create_contact():
    """Створює контакт з кириличними символами"""
    print("👤 Створення контакту з кириличними символами...")
    
    contact_data = {
        "first_name": "Олена",
        "last_name": "Сидоренко",
        "email": "olena@example.com",
        "phone": "+380631234567",
        "birth_date": "1988-06-15",
        "additional_data": "Новий контакт з українськими символами"
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/contacts/",
            json=contact_data,
            headers={"Content-Type": "application/json; charset=utf-8"}
        )
        
        print(f"✅ Статус: {response.status_code}")
        print(f"📄 Заголовки відповіді: {dict(response.headers)}")
        
        if response.status_code == 200:
            created_contact = response.json()
            print("📄 Створений контакт:")
            print(json.dumps(created_contact, indent=2, ensure_ascii=False))
            
            # Перевірка кодування
            if created_contact.get("first_name") == "Олена":
                print("✅ Кириличні символи збережені правильно!")
            else:
                print("❌ Проблема з кодуванням при збереженні")
        else:
            print(f"❌ Помилка: {response.text}")
            
    except Exception as e:
        print(f"❌ Помилка: {e}")

if __name__ == "__main__":
    create_contact() 