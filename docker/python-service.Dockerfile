ARG SERVICE_DIR
FROM python:3.11-slim

ARG SERVICE_DIR
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY ${SERVICE_DIR}/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r /app/requirements.txt
RUN python -c "import importlib.util, subprocess, sys; sys.exit(0) if importlib.util.find_spec('playwright') is None else subprocess.check_call([sys.executable, '-m', 'playwright', 'install', 'chromium'])"

COPY shared /app/shared
COPY ${SERVICE_DIR} /app

ENV PYTHONPATH=/app
CMD ["python", "main.py"]
