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
- **OpenAI Python SDK** or **Anthropic SDK**
  - AI-powered summary generation
  - Structured prompt handling
  - Streaming support

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
- **Poetry** or **pip + requirements.txt**
  - Current: pyproject.toml suggests Poetry
  - Dependency resolution
  - Virtual environment management

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
OPENAI_API_KEY=your_openai_key_here
# or
ANTHROPIC_API_KEY=your_anthropic_key_here
AI_MODEL=gpt-4-turbo-preview

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
- Poetry (for dependency management)
- Git
- Vercel account with API access
- OpenAI or Anthropic API key
- SMTP email account

### Installation Steps
```powershell
# Clone repository
git clone <repository-url>
cd Vercel-Web-Analytics-Report-Sender

# Install dependencies
poetry install

# Copy environment template
cp .env.example .env
# Edit .env with your credentials

# Run tests
poetry run pytest

# Run application
poetry run python main.py
```

## API Documentation

### Vercel Analytics API
- **Endpoint**: `https://vercel.com/api/web/insights`
- **Authentication**: Bearer token
- **Rate Limits**: Check Vercel documentation
- **Documentation**: https://vercel.com/docs/rest-api

### OpenAI API
- **Endpoint**: `https://api.openai.com/v1/chat/completions`
- **Models**: gpt-4-turbo-preview, gpt-3.5-turbo
- **Documentation**: https://platform.openai.com/docs

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
