FROM python:3.11

# Установка рабочей директории
WORKDIR /app

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование проекта
COPY . .

# Команда для запуска
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]