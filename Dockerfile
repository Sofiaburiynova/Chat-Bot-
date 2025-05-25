FROM python:3.11-slim

WORKDIR /app

# Ставим зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем твой бот
COPY main.py .

# Запуск
CMD ["python", "main.py"]
