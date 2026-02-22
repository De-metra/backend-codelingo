FROM python:3.12-slim

# Устанавливаем node
RUN apt-get update && apt-get install -y nodejs npm

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt

# 1. Копируем скрипт в контейнер
COPY entrypoint.sh .

# 2. Даем права на выполнение скрипта
RUN chmod +x entrypoint.sh

# 3. Указываем скрипт как точку входа
ENTRYPOINT ["./entrypoint.sh"]