# Vercel Web Analytics Report Sender

Automated Python application that fetches Vercel web analytics data, generates AI-powered summaries, and delivers professional reports via email on a scheduled basis.

## 🎯 Features

- **Automated Scheduling**: Runs every 30 days (configurable) without manual intervention
- **Vercel Integration**: Fetches comprehensive analytics data via Vercel API
- **AI-Powered Summaries**: Generates human-readable insights using Google Gemini
- **Email Delivery**: Sends professional formatted reports via SMTP
- **Secure Configuration**: Environment-based configuration with no hardcoded secrets
- **Comprehensive Logging**: Detailed logs for monitoring and debugging
- **Error Handling**: Robust retry logic and error notifications

## 📋 Prerequisites

- Python 3.11 or higher
- Vercel account with API access
- Google Gemini API key
- SMTP email account (Gmail, SendGrid, etc.)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Vercel-Web-Analytics-Report-Sender
```

### 2. Install Dependencies

Using uv (recommended):
```bash
uv sync
```

Or using pip:
```bash
pip install -e .
```

### 3. Configure Environment

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` and add your credentials:
- Vercel API token (from https://vercel.com/account/tokens)
- Vercel team ID and project ID
- Google Gemini API key
- SMTP email credentials

### 4. Run the Application

```bash
python main.py
```

## 📁 Project Structure

```
Vercel-Web-Analytics-Report-Sender/
├── .env                          # Environment variables (gitignored)
├── .env.example                  # Template for environment variables
├── main.py                       # Application entry point
├── pyproject.toml                # Dependencies and configuration
├── README.md                     # This file
├── memory-bank/                  # Project documentation
│   ├── projectbrief.md
│   ├── productContext.md
│   ├── systemPatterns.md
│   ├── techContext.md
│   ├── activeContext.md
│   ├── progress.md
│   └── journal/
├── src/                          # Source code
│   ├── config.py                 # Configuration management
│   ├── scheduler.py              # Job scheduling
│   ├── vercel/                   # Vercel API integration
│   ├── ai/                       # AI summary generation
│   ├── email/                    # Email delivery
│   ├── processing/               # Data processing
│   └── utils/                    # Utilities
├── tests/                        # Test suite
└── logs/                         # Application logs (gitignored)
```

## 🔧 Configuration

### Required Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `VERCEL_API_TOKEN` | Vercel API authentication token | `abc123...` |
| `VERCEL_TEAM_ID` | Your Vercel team ID | `team_abc123` |
| `VERCEL_PROJECT_ID` | Your Vercel project ID | `prj_abc123` |
| `TARGET_WEBSITE` | Website to track | `www.lemolegal.sk` |
| `GOOGLE_API_KEY` | Google Gemini API key | `AIza...` |
| `SMTP_HOST` | SMTP server hostname | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP server port | `587` |
| `SMTP_USERNAME` | SMTP username | `your@email.com` |
| `SMTP_PASSWORD` | SMTP password/app password | `****` |
| `EMAIL_TO` | Report recipient email | `recipient@example.com` |

See `.env.example` for all available configuration options.

## 🏗️ Architecture

The application follows a modular pipeline architecture:

```
Scheduler → Orchestrator → Vercel Data Extractor → Data Processor 
→ AI Summary Engine → Email Delivery Service
```

### Components

- **Scheduler**: APScheduler-based job scheduling
- **Vercel Data Extractor**: Fetches analytics via Vercel API
- **Data Processor**: Calculates metrics and trends
- **AI Summary Engine**: Generates natural language summaries
- **Email Delivery**: Sends formatted reports via SMTP
- **Configuration Manager**: Handles environment variables and settings

## 🧪 Testing

Run tests:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=src --cov-report=html
```

## 📊 Analytics Metrics

The reports include:

- Total page views and unique visitors
- Top pages and routes
- Traffic sources and referrers
- Geographic distribution
- Device and browser breakdown
- Period-over-period comparisons
- AI-generated insights and trends

## 🔒 Security

- All credentials stored in `.env` file (gitignored)
- No hardcoded secrets in code
- HTTPS for all API communications
- TLS for SMTP connections
- API keys never logged

## 🐛 Troubleshooting

### Common Issues

**"Authentication failed" error**
- Verify your Vercel API token is correct
- Check token has required permissions

**"SMTP authentication failed"**
- For Gmail, use App Password instead of regular password
- Enable "Less secure app access" if needed

**"Module not found" errors**
- Ensure dependencies are installed: `pip install -e .`
- Check Python version: `python --version` (must be 3.11+)

### Logs

Check application logs in `logs/app.log` for detailed error information.

## 📝 Development

### Code Quality

Format code:
```bash
black src/ tests/
```

Lint code:
```bash
ruff check src/ tests/
```

Type check:
```bash
mypy src/
```

### Pre-commit Hooks

Install pre-commit hooks:
```bash
pre-commit install
```

## 🚀 Deployment

### Local Server

Run as a background service using systemd (Linux) or Task Scheduler (Windows).

### Docker

```bash
docker build -t vercel-analytics-reporter .
docker run -d --env-file .env vercel-analytics-reporter
```

### Cloud Functions

Deploy to AWS Lambda, Google Cloud Functions, or Azure Functions with scheduled triggers.

## 📖 Documentation

Comprehensive project documentation is available in the `memory-bank/` directory:

- **projectbrief.md**: Project overview and objectives
- **productContext.md**: Problem statement and use cases
- **systemPatterns.md**: Architecture and design patterns
- **techContext.md**: Technology stack and setup
- **activeContext.md**: Current development status
- **progress.md**: Development progress tracker

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## 📄 License

[Add your license here]

## 🙋 Support

For issues and questions:
- Check the troubleshooting section above
- Review logs in `logs/app.log`
- Open an issue on GitHub

## 🗺️ Roadmap

- [ ] Support for multiple websites
- [ ] Web dashboard for report viewing
- [ ] Custom metric definitions
- [ ] Data visualizations in emails
- [ ] Slack/Discord integration
- [ ] Historical trend analysis
- [ ] Anomaly detection

---

**Built with ❤️ using Python, OpenAI, and Vercel API**
