import requests
import json
import time

# Налаштування
BASE_URL = "http://localhost:8000"

def print_step(step_num, description):
    print(f"\n{'='*50}")
    print(f"КРОК {step_num}: {description}")
    print(f"{'='*50}")

def print_success(message):
    print(f"✅ {message}")

def print_error(message):
    print(f"❌ {message}")

def print_info(message):
    print(f"ℹ️ {message}")

def test_auth_system():
    print("🔐 ПЕРЕВІРКА СИСТЕМИ АУТЕНТИФІКАЦІЇ")
    print("=" * 60)
    
    # Крок 1: Реєстрація нового користувача
    print_step(1, "РЕЄСТРАЦІЯ КОРИСТУВАЧА")
    
    register_data = {
        "email": f"test_{int(time.time())}@example.com",
        "password": "testpassword123"
    }
    
    print_info(f"Спроба реєстрації з email: {register_data['email']}")
    response = requests.post(f"{BASE_URL}/register", json=register_data)
    
    if response.status_code == 201:
        print_success("Користувач успішно зареєстрований!")
        user_data = response.json()
        print_info(f"ID користувача: {user_data['id']}")
        print_info(f"Email: {user_data['email']}")
    else:
        print_error(f"Помилка реєстрації: {response.status_code}")
        print_error(f"Деталі: {response.text}")
        return
    
    # Крок 2: Логін користувача
    print_step(2, "ЛОГІН КОРИСТУВАЧА")
    
    login_data = {
        "email": register_data["email"],
        "password": register_data["password"]
    }
    
    print_info("Спроба входу в систему...")
    response = requests.post(f"{BASE_URL}/login", json=login_data)
    
    if response.status_code == 200:
        print_success("Успішний вхід!")
        token_data = response.json()
        access_token = token_data['access_token']
        refresh_token = token_data['refresh_token']
        print_info(f"Access token отримано: {access_token[:30]}...")
        print_info(f"Refresh token отримано: {refresh_token[:30]}...")
    else:
        print_error(f"Помилка входу: {response.status_code}")
        print_error(f"Деталі: {response.text}")
        return
    
    # Крок 3: Створення контакту з аутентифікацією
    print_step(3, "СТВОРЕННЯ КОНТАКТУ (З АУТЕНТИФІКАЦІЄЮ)")
    
    contact_data = {
        "first_name": "Іван",
        "last_name": "Петренко",
        "email": "ivan.petrenko@example.com",
        "phone": "+380501234567",
        "birth_date": "1990-05-15",
        "additional_data": "Тестовий контакт"
    }
    
    headers = {"Authorization": f"Bearer {access_token}"}
    print_info("Спроба створення контакту...")
    response = requests.post(f"{BASE_URL}/contacts/", json=contact_data, headers=headers)
    
    if response.status_code == 201:
        print_success("Контакт успішно створено!")
        contact = response.json()
        print_info(f"ID контакту: {contact['id']}")
        print_info(f"Ім'я: {contact['first_name']} {contact['last_name']}")
    else:
        print_error(f"Помилка створення контакту: {response.status_code}")
        print_error(f"Деталі: {response.text}")
        return
    
    # Крок 4: Отримання списку контактів
    print_step(4, "ОТРИМАННЯ СПИСКУ КОНТАКТІВ")
    
    print_info("Запит списку контактів...")
    response = requests.get(f"{BASE_URL}/contacts/", headers=headers)
    
    if response.status_code == 200:
        print_success("Список контактів отримано!")
        contacts = response.json()
        print_info(f"Кількість контактів: {len(contacts)}")
        for contact in contacts:
            print_info(f"  - {contact['first_name']} {contact['last_name']} ({contact['email']})")
    else:
        print_error(f"Помилка отримання контактів: {response.status_code}")
        print_error(f"Деталі: {response.text}")
    
    # Крок 5: Спроба доступу без аутентифікації
    print_step(5, "ПЕРЕВІРКА БЛОКУВАННЯ НЕАВТОРИЗОВАНОГО ДОСТУПУ")
    
    print_info("Спроба доступу без токена...")
    response = requests.get(f"{BASE_URL}/contacts/")
    
    if response.status_code == 401:
        print_success("Неавторизований доступ правильно заблоковано!")
    elif response.status_code == 403:
        print_success("Неавторизований доступ заблоковано (403 Forbidden)")
    else:
        print_error(f"Неочікуваний статус: {response.status_code}")
        print_error("Система не заблокувала неавторизований доступ!")
    
    # Крок 6: Оновлення токена
    print_step(6, "ОНОВЛЕННЯ ТОКЕНА")
    
    refresh_data = {"refresh_token": refresh_token}
    print_info("Спроба оновлення токена...")
    response = requests.post(f"{BASE_URL}/refresh", json=refresh_data)
    
    if response.status_code == 200:
        print_success("Токен успішно оновлено!")
        new_tokens = response.json()
        print_info(f"Новий access token: {new_tokens['access_token'][:30]}...")
        print_info(f"Новий refresh token: {new_tokens['refresh_token'][:30]}...")
    else:
        print_error(f"Помилка оновлення токена: {response.status_code}")
        print_error(f"Деталі: {response.text}")
    
    # Крок 7: Тест дублікату email
    print_step(7, "ПЕРЕВІРКА ОБРОБКИ ДУБЛІКАТУ EMAIL")
    
    print_info("Спроба реєстрації з існуючим email...")
    response = requests.post(f"{BASE_URL}/register", json=register_data)
    
    if response.status_code == 409:
        print_success("Правильно оброблено дублікат email (409 Conflict)!")
    else:
        print_error(f"Неочікуваний статус для дублікату: {response.status_code}")
    
    # Крок 8: Тест неправильного пароля
    print_step(8, "ПЕРЕВІРКА НЕПРАВИЛЬНОГО ПАРОЛЯ")
    
    wrong_login_data = {
        "email": register_data["email"],
        "password": "wrongpassword"
    }
    
    print_info("Спроба входу з неправильним паролем...")
    response = requests.post(f"{BASE_URL}/login", json=wrong_login_data)
    
    if response.status_code == 401:
        print_success("Правильно оброблено неправильний пароль (401 Unauthorized)!")
    else:
        print_error(f"Неочікуваний статус для неправильного пароля: {response.status_code}")
    
    print("\n" + "="*60)
    print("🎉 ПЕРЕВІРКА ЗАВЕРШЕНА!")
    print("="*60)

if __name__ == "__main__":
    try:
        test_auth_system()
    except requests.exceptions.ConnectionError:
        print("❌ Помилка підключення до сервера!")
        print("ℹ️ Переконайтеся, що сервер запущено: python run.py")
    except Exception as e:
        print(f"❌ Неочікувана помилка: {e}") 