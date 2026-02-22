FROM python:3.12-slim

# Устанавливаем node
RUN apt-get update && apt-get install -y nodejs npm

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10000"]