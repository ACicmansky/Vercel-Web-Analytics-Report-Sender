# System Patterns

## Architecture Overview
Modular, pipeline-based architecture following separation of concerns principle.

```
┌─────────────┐
│  Scheduler  │ (APScheduler or Cron)
└──────┬──────┘
       │ Triggers every 30 days
       ▼
┌─────────────────────┐
│ Orchestrator/Main   │
└──────┬──────────────┘
       │
       ├──────────────────────────────────┐
       │                                  │
       ▼                                  ▼
┌──────────────────┐            ┌─────────────────┐
│ Vercel Data      │            │ Configuration   │
│ Extractor        │◄───────────┤ Manager         │
└────────┬─────────┘            └─────────────────┘
         │                               │
         │ Raw Analytics Data            │ API Keys, Settings
         ▼                               │
┌──────────────────┐                     │
│ Data Processing  │                     │
│ & AI Summary     │◄────────────────────┘
│ Engine           │
└────────┬─────────┘
         │ Generated Summary
         ▼
┌──────────────────┐
│ Email Delivery   │
│ Service          │
└──────────────────┘
```

## Core Design Patterns

### 1. Modular Pipeline Pattern
Each component is independent and testable:
- **Vercel Data Extractor**: Single responsibility - API communication
- **Data Processor**: Transforms raw data into structured metrics
- **AI Summary Engine**: Generates natural language summaries
- **Email Service**: Handles delivery logic

### 2. Configuration Management Pattern
- Centralized configuration via `.env` file
- Environment variables for sensitive data
- Type-safe configuration loading
- Validation on startup

### 3. Error Handling Strategy
- Try-catch blocks at module boundaries
- Structured logging for debugging
- Graceful degradation where possible
- Retry logic for transient failures
- Email notifications for critical errors

### 4. Dependency Injection
- Pass configuration objects to modules
- Facilitates testing with mock objects
- Reduces tight coupling

## Component Responsibilities

### Scheduler
- **Purpose**: Trigger the reporting pipeline
- **Technology**: APScheduler (Python) or system cron
- **Responsibilities**:
  - Execute main orchestrator on schedule
  - Handle timezone considerations
  - Log execution times

### Vercel Data Extractor
- **Purpose**: Interface with Vercel API
- **Responsibilities**:
  - Authenticate using API token
  - Fetch analytics data for specified date range
  - Handle rate limiting
  - Parse API responses
  - Return structured data

### Data Processing & AI Summary Engine
- **Purpose**: Transform data and generate insights
- **Responsibilities**:
  - Calculate key metrics (totals, averages, trends)
  - Compare with previous period
  - Identify significant changes
  - Generate AI prompt with structured data
  - Call AI API (OpenAI, Anthropic, etc.)
  - Format AI response

### Email Delivery Service
- **Purpose**: Send formatted reports
- **Responsibilities**:
  - Format email content (HTML/plain text)
  - Attach or embed data visualizations
  - Send via SMTP
  - Handle delivery failures
  - Log delivery status

### Configuration Manager
- **Purpose**: Centralize settings management
- **Responsibilities**:
  - Load environment variables
  - Validate required settings
  - Provide typed access to configuration
  - Secure credential handling

## Data Flow

1. **Trigger**: Scheduler initiates process
2. **Configuration Load**: Load API keys, settings
3. **Data Fetch**: Request analytics from Vercel API
4. **Data Transform**: Process raw data into metrics
5. **AI Generation**: Create summary from metrics
6. **Email Composition**: Format report email
7. **Delivery**: Send email via SMTP
8. **Logging**: Record execution results

## Key Technical Decisions

### Why APScheduler over Cron?
- Platform-independent (works on Windows/Linux)
- Python-native (easier debugging)
- Programmatic control
- Better for development/testing

### Why Modular Architecture?
- Testability: Each module can be unit tested
- Maintainability: Changes isolated to specific modules
- Reusability: Modules can be reused for other projects
- Scalability: Easy to add new features or websites

### Error Recovery Strategy
- **Transient Errors**: Retry with exponential backoff
- **API Rate Limits**: Respect limits, queue requests
- **Critical Failures**: Log and notify via email
- **Partial Failures**: Continue with available data

## Security Patterns

### Credential Management
- Never commit secrets to version control
- Use `.env` file (gitignored)
- Environment variables in production
- Consider secrets management service for production

### API Security
- Use HTTPS for all API calls
- Validate SSL certificates
- Rotate API keys periodically
- Implement request signing if available

### Email Security
- Use TLS for SMTP connections
- Validate recipient addresses
- Sanitize content to prevent injection
- Rate limit to prevent abuse

## Testing Strategy

### Unit Tests
- Test each module independently
- Mock external dependencies (API, SMTP)
- Test error handling paths

### Integration Tests
- Test module interactions
- Use test API credentials
- Verify end-to-end flow

### Manual Testing
- Test with real Vercel API
- Verify email delivery
- Check AI summary quality
