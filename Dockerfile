FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
COPY src/ ./src/
COPY main.py .

RUN pip install --no-cache-dir -r requirements.txt

# Defaults to device code in the Docker build. I don't think opening a browser in a container will work well so if you want to auth with the SDK, use the non-container version
CMD ["python", "main.py"]