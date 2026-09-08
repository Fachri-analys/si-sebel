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
  CMD python -c "import pathlib; raise SystemExit(0 if pathlib.Path('/app/run_bot.py').is_file() else 1)"

# Jalankan bot
CMD ["python", "run_bot.py"]