FROM python:3.11-slim

WORKDIR /app

# System deps (optional: add poppler-utils if advanced PDF parsing later)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
  && rm -rf /var/lib/apt/lists/*

# Copy and install resume-service requirements
COPY services/resume-service/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install shared requirements if present
COPY shared/requirements.txt /tmp/shared_requirements.txt
RUN pip install --no-cache-dir -r /tmp/shared_requirements.txt || true

# Copy service code and shared package
COPY services/resume-service /app
COPY shared /app/shared

ENV PYTHONUNBUFFERED=1 \
    AUTO_CREATE_TABLES=1 \
    FEATURE_PARSE=1

EXPOSE 8003

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8003"]
