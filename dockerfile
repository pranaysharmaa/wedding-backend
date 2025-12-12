FROM python:3.11-slim

# Create working directory
WORKDIR /app

# Install deps first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy ONLY the "app" folder into /app/app inside image
COPY app ./app

# Copy scripts (optional)
COPY scripts ./scripts

# Expose PYTHONPATH cleanly
ENV PYTHONPATH=/app

# NO reload in Docker image (reload only via docker-compose)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
