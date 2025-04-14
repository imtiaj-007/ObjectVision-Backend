# Stage 1: Builder
FROM python:3.10-slim AS builder
WORKDIR /build

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libgl1 \
    libsndfile1 \
    ffmpeg \
    curl && \
    rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy ONLY requirements first to leverage caching
COPY requirements.txt .

# Install dependencies - this layer only changes when requirements.txt changes
RUN pip install --upgrade pip && \
    (python -c "import torch, torchvision, torchaudio" || \
    pip install --no-cache-dir \
        torch==2.3.0+cpu \
        torchvision==0.18.0+cpu \
        torchaudio==2.3.0+cpu \
        -f https://download.pytorch.org/whl/torch_stable.html) && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install gunicorn==22.0.0 &&\
    pip check

# Stage 2: Runtime
FROM python:3.10-slim

# Create user with explicit UID/GID (matches host)
ARG USER_ID=1000
ARG GROUP_ID=1000
RUN addgroup --gid ${GROUP_ID} appuser && \
    adduser --disabled-password --gecos "" --uid ${USER_ID} --gid ${GROUP_ID} appuser

# Install runtime dependencies + supervisor
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libgl1 \
    libsndfile1 \
    ffmpeg \
    libpq5 \
    curl \
    libgomp1 \
    supervisor && \
    rm -rf /var/lib/apt/lists/*

# Configure supervisor directories with correct permissions
RUN mkdir -p /var/log/supervisor /var/run/supervisor && \
    chown -R appuser:appuser /var/log/supervisor /var/run/supervisor && \
    chmod -R 775 /var/log/supervisor /var/run/supervisor

# Environment config
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UVICORN_WORKERS=1 \
    GUNICORN_WORKERS=1 \
    GUNICORN_TIMEOUT=120 \
    GUNICORN_KEEPALIVE=1 \
    PYTHONPATH=/object-vision-backend \
    PATH="/opt/venv/bin:$PATH" \
    UMASK=002

# Create volume directories with correct permissions
RUN mkdir -p /object-vision-backend/{uploads,logs,ML_models,output,cache/image} && \
    chown -R appuser:appuser /object-vision-backend && \
    chmod -R 775 /object-vision-backend

# Copy virtual environment
COPY --from=builder --chown=appuser:appuser /opt/venv /opt/venv

# Copy supervisor config first (rarely changes)
COPY --chown=root:root supervisord.conf /etc/supervisor/conf.d/supervisord.conf
RUN chmod 644 /etc/supervisor/conf.d/supervisord.conf

# Copy app code LAST (changes most frequently)
WORKDIR /object-vision-backend
COPY --chown=appuser:appuser . .

USER appuser
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://127.0.0.1:8000/health || exit 1

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf", "--user=appuser"]