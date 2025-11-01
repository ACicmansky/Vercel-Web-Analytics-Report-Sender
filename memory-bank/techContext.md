# Technical Context

## Technology Stack

### Core Language
- **Python 3.11+**
  - Modern async/await support
  - Type hints for better code quality
  - Rich standard library

### Key Dependencies

#### Scheduling
- **APScheduler** (3.10+)
  - Background job scheduling
  - Cron-like scheduling
  - Persistent job stores

#### HTTP & API Communication
- **httpx** or **requests**
  - Vercel API communication
  - HTTP client with retry logic
  - Async support (httpx)

#### AI Integration
- **Google GenAI SDK** (google-genai>=0.2.0)
  - AI-powered summary generation using Gemini 2.5 Flash
  - Structured prompt handling
  - Cost-effective with free tier

#### Email Delivery
- **smtplib** (standard library) + **email** package
  - SMTP email sending
  - HTML email formatting
- **Alternative**: **SendGrid** or **Amazon SES** SDK

#### Configuration Management
- **python-dotenv**
  - Load environment variables from .env
  - Development/production configuration

#### Data Processing
- **pandas** (optional, for complex analytics)
  - Data manipulation
  - Statistical calculations
- **json** (standard library)
  - Parse API responses

#### Logging
- **logging** (standard library)
  - Structured logging
  - File and console handlers
- **loguru** (alternative)
  - Simplified logging interface

#### Testing
- **pytest**
  - Unit and integration testing
- **pytest-mock**
  - Mocking external dependencies
- **responses** or **httpx-mock**
  - Mock HTTP requests

### Development Tools

#### Dependency Management
- **uv** (modern Python package manager)
  - 10-100x faster than pip/Poetry
  - Better dependency resolution
  - Simpler workflow
  - Virtual environment management
  - Install: `pip install uv`
  - Usage: `uv sync`, `uv add package-name`

#### Code Quality
- **black** - Code formatting
- **ruff** - Fast linting
- **mypy** - Type checking
- **pre-commit** - Git hooks for quality checks

#### Version Control
- **Git**
  - Current: .git directory exists
  - GitHub/GitLab for remote repository

## Project Structure

```
Vercel-Web-Analytics-Report-Sender/
├── .env                          # Environment variables (gitignored)
├── .env.example                  # Template for environment variables
├── .gitignore                    # Git ignore rules
├── .python-version               # Python version specification
├── pyproject.toml                # Poetry dependencies and config
├── README.md                     # Project documentation
├── main.py                       # Application entry point
├── memory-bank/                  # Project memory and documentation
│   ├── projectbrief.md
│   ├── productContext.md
│   ├── systemPatterns.md
│   ├── techContext.md
│   ├── activeContext.md
│   ├── progress.md
│   └── journal/
├── src/                          # Source code
│   ├── __init__.py
│   ├── config.py                 # Configuration management
│   ├── scheduler.py              # Job scheduling logic
│   ├── vercel/
│   │   ├── __init__.py
│   │   ├── client.py             # Vercel API client
│   │   └── models.py             # Data models for analytics
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── summarizer.py         # AI summary generation
│   │   └── prompts.py            # AI prompt templates
│   ├── email/
│   │   ├── __init__.py
│   │   ├── sender.py             # Email sending logic
│   │   └── templates.py          # Email templates
│   ├── processing/
│   │   ├── __init__.py
│   │   └── analyzer.py           # Data processing and metrics
│   └── utils/
│       ├── __init__.py
│       ├── logger.py             # Logging configuration
│       └── retry.py              # Retry logic utilities
├── tests/                        # Test suite
│   ├── __init__.py
│   ├── test_vercel_client.py
│   ├── test_ai_summarizer.py
│   ├── test_email_sender.py
│   └── test_integration.py
└── logs/                         # Application logs (gitignored)
    └── app.log
```

## Environment Variables

Required configuration in `.env`:

```env
# Vercel Configuration
VERCEL_API_TOKEN=your_vercel_token_here
VERCEL_TEAM_ID=your_team_id_here
VERCEL_PROJECT_ID=your_project_id_here
TARGET_WEBSITE=www.lemolegal.sk

# AI Configuration
GOOGLE_API_KEY=your_google_gemini_key_here
AI_MODEL=gemini-2.5-flash

# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
EMAIL_FROM=your_email@gmail.com
EMAIL_TO=recipient@example.com
EMAIL_SUBJECT_PREFIX=[Analytics Report]

# Scheduling
REPORT_INTERVAL_DAYS=30
REPORT_TIME=09:00  # Time to send report (24h format)

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

## Development Setup

### Prerequisites
- Python 3.11 or higher
- uv package manager (install via `pip install uv`)
- Git
- Vercel account with API access
- Google Gemini API key (free tier available)
- SMTP email account (Gmail recommended)

### Installation Steps
```powershell
# Clone repository
git clone <repository-url>
cd Vercel-Web-Analytics-Report-Sender

# Install uv (if not already installed)
pip install uv

# Install dependencies
uv sync

# Copy environment template
Copy-Item .env.example .env
# Edit .env with your credentials

# Run tests
pytest

# Run application
python main.py
```

## API Documentation

### Vercel Analytics API
- **Endpoint**: `https://vercel.com/api/web/insights`
- **Authentication**: Bearer token
- **Rate Limits**: Check Vercel documentation
- **Documentation**: https://vercel.com/docs/rest-api

### Google Gemini API
- **Endpoint**: Via Google GenAI SDK
- **Models**: gemini-2.5-flash (recommended)
- **API Key**: https://aistudio.google.com/apikey
- **Documentation**: https://ai.google.dev/docs
- **Free Tier**: 15 requests per minute

## Technical Constraints

### Performance
- API rate limits must be respected
- Email sending should be throttled
- Large datasets may require pagination

### Security
- All secrets in environment variables
- No hardcoded credentials
- HTTPS for all external communications
- Secure SMTP connections (TLS)

### Reliability
- Implement retry logic for API calls
- Handle network failures gracefully
- Log all errors for debugging
- Email notification on critical failures

### Compatibility
- Cross-platform (Windows, Linux, macOS)
- Python 3.11+ required
- No OS-specific dependencies

## Deployment Considerations

### Local Development
- Use `.env` file for configuration
- Run manually or with scheduler
- Logs to console and file

### Production Deployment Options

#### Option 1: VPS/Server
- Deploy on Linux server
- Use systemd for service management
- Cron or APScheduler for scheduling

#### Option 2: Cloud Functions
- AWS Lambda with EventBridge
- Google Cloud Functions with Cloud Scheduler
- Azure Functions with Timer Trigger

#### Option 3: Container
- Docker container
- Kubernetes CronJob
- Docker Compose for local testing

### Monitoring
- Log aggregation (e.g., CloudWatch, Datadog)
- Error tracking (e.g., Sentry)
- Email delivery monitoring
- API usage tracking
