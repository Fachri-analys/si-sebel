FROM python:3.12-slim

WORKDIR /app

# Install system dependencies (opsional, untuk kompilasi)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/data /app/piwapp_auth \
    && useradd --create-home --uid 10001 appuser \
    && chown -R appuser:appuser /app
USER appuser
STOPSIGNAL SIGTERM
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python scripts/healthcheck.py --database /app/data/sisebel.db --auth-folder /app/piwapp_auth

# Jalankan bot
CMD ["python", "run_bot.py"]