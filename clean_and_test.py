#!/usr/bin/env python3
"""
Очищення бази даних та тестування
"""
import requests
import json

def clean_and_test():
    """Очищає базу даних та тестує кодування"""
    print("🧹 Очищення бази даних...")
    
    # Отримуємо всі контакти
    response = requests.get("http://localhost:8000/contacts/")
    if response.status_code == 200:
        contacts = response.json()
        
        # Видаляємо всі контакти
        for contact in contacts:
            contact_id = contact.get("id")
            if contact_id:
                delete_response = requests.delete(f"http://localhost:8000/contacts/{contact_id}")
                print(f"🗑️ Видалено контакт ID {contact_id}: {delete_response.status_code}")
    
    print("\n👤 Створення нових контактів з правильним кодуванням...")
    
    # Створюємо нові контакти
    contacts_data = [
        {
            "first_name": "Іван",
            "last_name": "Петренко",
            "email": "ivan@example.com",
            "phone": "+380501234567",
            "birth_date": "1990-01-15",
            "additional_data": "Розробник з України"
        },
        {
            "first_name": "Марія",
            "last_name": "Коваленко",
            "email": "maria@example.com",
            "phone": "+380671234567",
            "birth_date": "1985-03-20",
            "additional_data": "Дизайнер з Києва"
        },
        {
            "first_name": "Олег",
            "last_name": "Сидоренко",
            "email": "oleg@example.com",
            "phone": "+380631234567",
            "birth_date": "1992-07-10",
            "additional_data": "Менеджер з Львова"
        }
    ]
    
    for contact_data in contacts_data:
        response = requests.post(
            "http://localhost:8000/contacts/",
            json=contact_data,
            headers={"Content-Type": "application/json; charset=utf-8"}
        )
        
        if response.status_code == 200:
            created_contact = response.json()
            print(f"✅ Створено: {created_contact['first_name']} {created_contact['last_name']}")
        else:
            print(f"❌ Помилка створення: {response.text}")
    
    print("\n📋 Перевірка всіх контактів...")
    response = requests.get("http://localhost:8000/contacts/")
    if response.status_code == 200:
        contacts = response.json()
        print("📄 Всі контакти:")
        print(json.dumps(contacts, indent=2, ensure_ascii=False))
        
        # Перевіряємо кодування
        all_correct = True
        for contact in contacts:
            if "?" in contact.get("first_name", "") or "?" in contact.get("last_name", ""):
                all_correct = False
                break
        
        if all_correct:
            print("✅ Всі контакти мають правильне кодування!")
        else:
            print("❌ Є проблеми з кодуванням")
    else:
        print(f"❌ Помилка отримання контактів: {response.text}")

if __name__ == "__main__":
    clean_and_test() 