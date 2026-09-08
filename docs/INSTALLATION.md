# Installation Guide - Si Sebel Bot

## Prerequisites

### System Requirements
- **Python 3.12+** (REQUIRED - piwapp library requires Python 3.12+)
- Pip (Python package manager)
- Git
- Redis Server (for caching) - See Redis Setup section
- 500MB free disk space
- Stable internet connection

### Check Python Version
```bash
python --version
# or
python3 --version
```

If your Python version is lower than 3.12, you need to upgrade Python first.

## Redis Setup

Redis is required for caching. Choose one of the following setup methods:

### Option 1: Docker (Recommended)

```bash
docker run -d -p 6379:6379 --name sisebel-redis redis:7-alpine
```

Or use Docker Compose (included):
```bash
docker-compose up -d redis
```

### Option 2: System Installation

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install redis-server
sudo systemctl start redis
sudo systemctl enable redis
```

**Windows:**
Download Redis for Windows from: https://github.com/microsoftarchive/redis/releases

### Option 3: Disable Caching

If you don't want to use Redis, set in `config/.env`:
```env
ENABLE_CACHE=false
```

## Installation Steps

### 1. Clone or Download Project

If using Git:
```bash
git clone <repository-url>
cd si-sebel
```

Or download and extract the project folder.

### 2. Create Virtual Environment (Recommended)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.lock
```

If you encounter any issues, try:
```bash
pip install --upgrade pip
pip install -r requirements.lock
```

### 4. Setup Configuration

Copy the example environment file:
```bash
copy config\.env.example config\.env
```

Edit `config/.env` with your preferred settings:
```env
# WhatsApp Configuration
WHATSAPP_PHONE_NUMBER=628xxxxxxxxxx

# Bot Configuration
BOT_NAME=Si Sebel
BOT_RESPONSE_DELAY=3

# Database Configuration
DATABASE_PATH=sisebel.db

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/sisebel.log

# Development/Production Mode
ENVIRONMENT=development

# Redis Configuration (Caching)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
CACHE_TTL=3600  # Cache time-to-live in seconds (1 hour)
ENABLE_CACHE=true

# Load Balancing Configuration
MAX_INSTANCES=1  # Number of bot instances (for future scaling)
MAX_CONNECTIONS=50  # Max concurrent connections per instance
MAX_REQUESTS=100  # Max requests per time window (rate limiting)
RATE_LIMIT_WINDOW=60  # Rate limit time window in seconds
```

### 5. Verify Installation

Check if all dependencies are installed:
```bash
pip list
```

You should see:
- piwapp
- python-dotenv
- pydantic
- pydantic-settings
- colorlog
- redis
- hiredis (optional, for faster Redis parsing)

## Running the Bot

### Option 1: Direct Python (Development)

#### First Time Setup

### First Time Setup

1. Run the bot:
```bash
python run_bot.py
```

2. The bot will display a QR code in the terminal. Scan this QR code with your WhatsApp:
   - Open WhatsApp on your phone
   - Go to Settings → Linked Devices
   - Link a Device
   - Scan the QR code

3. Once connected, you'll see "✓ Online as <your phone number>"

### Option 2: Docker Compose (Production)

**Build and start all services:**
```bash
docker-compose up -d
```

**View logs:**
```bash
docker-compose logs -f bot
```

**Stop services:**
```bash
docker-compose down
```

**Rebuild after changes:**
```bash
docker-compose up -d --build
```

### Normal Usage

After the first-time setup, simply run:
```bash
python run_bot.py
```

The bot will automatically reconnect using saved credentials.

## Troubleshooting

### Python Version Issue
**Error:** "piwapp requires Python 3.12+"

**Solution:** Upgrade Python to version 3.12 or higher from python.org

### Import Error
**Error:** "ModuleNotFoundError: No module named 'piwapp'"

**Solution:**
```bash
pip install piwapp
```

### Database Error
**Error:** "Failed to initialize database"

**Solution:**
- Check if you have write permissions in the project directory
- Delete the existing database file and try again
- Check database path in config/.env

### WhatsApp Connection Error
**Error:** "Failed to connect to WhatsApp"

**Solution:**
- Ensure you have stable internet connection
- Delete the `piwapp_auth` folder and try again (requires re-scanning QR)
- Check if WhatsApp service is available

### Redis Connection Error
**Error:** "Failed to connect to Redis"

**Solution:**
- Ensure Redis is running: `redis-cli ping` (should return PONG)
- Check Redis host and port in config/.env
- If using Docker, ensure Redis container is running: `docker ps`
- If Redis password is set, ensure it's configured correctly
- For development, you can disable caching: `ENABLE_CACHE=false` in config/.env

### QR Code Not Displaying
**Error:** QR code doesn't appear in terminal

**Solution:**
- Check if terminal supports Unicode/ASCII
- Try using a different terminal (Git Bash, PowerShell, etc.)
- The QR code is also saved as `piwapp_qr.png` in the project directory

## Development Setup

### For Development

1. Create development environment:
```bash
python -m venv venv-dev
venv-dev\Scripts\activate  # Windows
# or
source venv-dev/bin/activate  # Linux/Mac
```

2. Install development dependencies:
```bash
pip install -r requirements.lock
pip install pytest pytest-asyncio black flake8
```

### Code Formatting

Format code with Black:
```bash
black src/
```

### Linting

Check code with Flake8:
```bash
flake8 src/
```

### Testing

Run tests (when available):
```bash
pytest tests/
```

## Uninstallation

To remove the bot:

1. Deactivate virtual environment:
```bash
deactivate
```

2. Delete virtual environment folder:
```bash
# Windows
rmdir /s venv

# Linux/Mac
rm -rf venv
```

3. Delete project folder (optional)

## Updating Dependencies

To update dependencies:
```bash
pip install --upgrade -r requirements.lock
```

## Security Notes

- Never commit the `config/.env` file to version control
- Never share your WhatsApp authentication files (`piwapp_auth/`)
- Use a dedicated WhatsApp number for the bot, not your personal number
- Regularly backup your database file

## Support

For issues or questions:
1. Check this installation guide
2. Check the main README.md
3. Check the documentation in docs/ folder
4. Contact the development team