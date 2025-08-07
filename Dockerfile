FROM python:3.11-slim

# Встановлення системних залежностей
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Встановлення робочої директорії
WORKDIR /app

# Копіювання файлів залежностей
COPY requirements.txt .

# Встановлення Python залежностей
RUN pip install --no-cache-dir -r requirements.txt

# Копіювання коду додатку
COPY . .

# Створення не-root користувача
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Відкриття порту
EXPOSE 8000

# Команда запуску
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"] 