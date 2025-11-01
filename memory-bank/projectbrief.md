# Project Brief: Vercel Web Analytics Report Sender

## Project Overview
Automated Python application that periodically fetches Vercel Web Analytics data, generates AI-powered summaries, and delivers reports via email.

## Core Objective
Create a scheduled service that runs every 30 days to:
1. Download web analytics data from Vercel for www.lemolegal.sk
2. Generate AI-powered summary of the analytics
3. Send formatted email report to designated recipients

## Target Website
- Primary: www.lemolegal.sk

## Key Requirements

### Functional Requirements
- **Automated Scheduling**: Execute every 30 days without manual intervention
- **Data Extraction**: Fetch analytics from Vercel API (page views, visitors, top sources, etc.)
- **AI Analysis**: Generate human-readable summaries from raw analytics data
- **Email Delivery**: Send professional formatted reports via email
- **Configuration Management**: Secure storage of API keys, email settings, and website configurations

### Non-Functional Requirements
- **Security**: Secure handling of API keys and credentials
- **Reliability**: Robust error handling and logging
- **Maintainability**: Modular architecture for easy updates
- **Scalability**: Designed to support multiple websites in the future

## Success Criteria
- System successfully runs on 30-day schedule
- Analytics data accurately retrieved from Vercel
- AI summaries are coherent and actionable
- Emails delivered successfully to recipients
- All credentials stored securely

## Constraints
- Python-based implementation
- Must use Vercel API for data extraction
- Email delivery via SMTP service
- Configuration via environment variables or secure config files

## Out of Scope (Initial Version)
- Real-time analytics monitoring
- Web dashboard/UI
- Multiple website support (future enhancement)
- Custom analytics metrics beyond Vercel's standard offerings
