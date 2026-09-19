FROM python:3.11-slim

# Prevent Python from creating .pyc files
ENV PYTHONDONTWRITEBYTECODE=1

# Send Python output directly to terminal
ENV PYTHONUNBUFFERED=1

# Don't create pip cache
ENV PIP_NO_CACHE_DIR=1

WORKDIR /workspace

# Install only what is necessary
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first
# This creates a Docker cache layer.
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Copy the project into the image so it can also run without a bind mount.
COPY . .

EXPOSE 8501
EXPOSE 8888

# Default command
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]