#!/usr/bin/env python3
"""
Скрипт для ініціалізації бази даних PostgreSQL
"""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from config import settings
import os

def create_database():
    """Створює базу даних PostgreSQL якщо вона не існує"""
    # Парсимо URL бази даних
    db_url = settings.DATABASE_URL
    if db_url.startswith('postgresql://'):
        db_url = db_url.replace('postgresql://', '')
    
    # Розбираємо компоненти URL
    if '@' in db_url:
        auth_part, rest = db_url.split('@', 1)
        if ':' in auth_part:
            username, password = auth_part.split(':', 1)
        else:
            username, password = auth_part, ''
        
        if ':' in rest:
            host_port, db_name = rest.rsplit('/', 1)
            if ':' in host_port:
                host, port = host_port.split(':', 1)
            else:
                host, port = host_port, '5432'
        else:
            host, port = rest.split('/', 1)
            db_name = rest.split('/')[-1]
    else:
        # Простий формат
        parts = db_url.split('/')
        if len(parts) >= 2:
            db_name = parts[-1]
            host_port = parts[0]
            if ':' in host_port:
                host, port = host_port.split(':', 1)
            else:
                host, port = host_port, '5432'
            username = password = ''
        else:
            print("Неправильний формат DATABASE_URL")
            return False

    try:
        # Підключаємося до PostgreSQL сервера
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=username,
            password=password,
            database='postgres'  # Підключаємося до стандартної бази
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Перевіряємо чи існує база даних
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
        exists = cursor.fetchone()
        
        if not exists:
            print(f"Створюю базу даних '{db_name}'...")
            cursor.execute(f'CREATE DATABASE "{db_name}"')
            print(f"База даних '{db_name}' успішно створена!")
        else:
            print(f"База даних '{db_name}' вже існує.")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Помилка при створенні бази даних: {e}")
        print("\nПереконайтеся що:")
        print("1. PostgreSQL сервер запущений")
        print("2. Користувач має права для створення баз даних")
        print("3. DATABASE_URL правильно налаштований")
        return False

if __name__ == "__main__":
    print("Ініціалізація бази даних PostgreSQL...")
    if create_database():
        print("База даних готова!")
    else:
        print("Помилка ініціалізації бази даних.") 