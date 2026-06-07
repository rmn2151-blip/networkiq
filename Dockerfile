# Optional: containerized run (works on Render, Hugging Face Spaces, Fly, etc.)
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Hosts inject $PORT; default to 8000 for local `docker run -p 8000:8000`.
ENV PORT=8000
EXPOSE 8000
CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port ${PORT}"]
