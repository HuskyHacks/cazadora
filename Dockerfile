FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
COPY src/ ./src/
COPY main.py .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]