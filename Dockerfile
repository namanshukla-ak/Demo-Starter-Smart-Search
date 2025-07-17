# Neurologix Smart Search POV - Multi-stage Dockerfile
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    pkg-config \
    default-libmysqlclient-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create logs directory
RUN mkdir -p logs

# Expose ports
EXPOSE 8000 8501

# Backend stage
FROM base as backend
WORKDIR /app/backend
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Frontend stage  
FROM base as frontend
WORKDIR /app
CMD ["streamlit", "run", "frontend.py", "--server.port", "8501", "--server.address", "0.0.0.0", "--server.headless", "true"]

# Development stage (runs both services)
FROM base as development
WORKDIR /app

# Install tmux for running multiple services
RUN apt-get update && apt-get install -y tmux && rm -rf /var/lib/apt/lists/*

# Copy startup script
COPY start_services.sh .
RUN chmod +x start_services.sh

# Create a startup script for Docker
RUN echo '#!/bin/bash\n\
    # Start backend in background\n\
    cd /app/backend && uvicorn main:app --host 0.0.0.0 --port 8000 --reload &\n\
    \n\
    # Wait a moment for backend to start\n\
    sleep 5\n\
    \n\
    # Start frontend\n\
    cd /app && streamlit run frontend.py --server.port 8501 --server.address 0.0.0.0 --server.headless true\n\
    ' > /app/docker-start.sh && chmod +x /app/docker-start.sh

CMD ["/app/docker-start.sh"]

# Production stage
FROM base as production
WORKDIR /app

# Install supervisor for process management
RUN apt-get update && apt-get install -y supervisor && rm -rf /var/lib/apt/lists/*

# Copy supervisor configuration
RUN echo '[supervisord]\n\
    nodaemon=true\n\
    logfile=/var/log/supervisor/supervisord.log\n\
    pidfile=/var/run/supervisord.pid\n\
    \n\
    [program:backend]\n\
    command=uvicorn main:app --host 0.0.0.0 --port 8000\n\
    directory=/app/backend\n\
    autostart=true\n\
    autorestart=true\n\
    stderr_logfile=/var/log/supervisor/backend.err.log\n\
    stdout_logfile=/var/log/supervisor/backend.out.log\n\
    \n\
    [program:frontend]\n\
    command=streamlit run frontend.py --server.port 8501 --server.address 0.0.0.0 --server.headless true\n\
    directory=/app\n\
    autostart=true\n\
    autorestart=true\n\
    stderr_logfile=/var/log/supervisor/frontend.err.log\n\
    stdout_logfile=/var/log/supervisor/frontend.out.log\n\
    ' > /etc/supervisor/conf.d/neurologix.conf

# Create log directories
RUN mkdir -p /var/log/supervisor

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/supervisord.conf"]
