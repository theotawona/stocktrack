# Use official Python runtime as base image
FROM python:3.11-slim

# Set working directory in container
WORKDIR /app

# Install curl for health check (build-essential not needed — all packages have pre-built wheels)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directory for persistent storage
RUN mkdir -p /app/data

# Set DB_PATH so the app writes to the persistent volume
ENV DB_PATH=/app/data/stock_tracker.db

# If a local DB exists, copy it into the data dir as a seed
# (only used on first deploy; volume mount will override)
RUN if [ -f /app/stock_tracker.db ]; then cp /app/stock_tracker.db /app/data/stock_tracker.db; fi

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Set environment variables for Streamlit
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_LOGGER_LEVEL=info

# Run Streamlit app
CMD ["streamlit", "run", "app.py", "--logger.level=info"]
