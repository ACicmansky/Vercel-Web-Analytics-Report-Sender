# Setup & Troubleshooting Reference

## Quick Start Commands

### Installation
```powershell
# Install uv package manager
pip install uv

# Install all dependencies
uv sync

# Configure environment
Copy-Item .env.example .env
# Edit .env with your credentials
```

### Testing & Running
```powershell
# Test all connections
python main.py --test

# Run report once
python main.py --run-once

# Start scheduler
python main.py

# Run immediately then schedule
python main.py --run-immediately

# Enable debug logging
python main.py --log-level DEBUG
```

## Required Credentials

### Google Analytics 4 API
- **Property ID**: From GA4 dashboard (Admin → Property Settings)
- **Service Account**: Create in Google Cloud Console
- **Setup Steps**:
  1. Go to [Google Cloud Console](https://console.cloud.google.com/)
  2. Create new project or select existing
  3. Enable "Google Analytics Data API"
  4. Create Service Account (IAM & Admin → Service Accounts)
  5. Download JSON credentials
  6. In GA4: Admin → Property Access Management
  7. Add service account email with "Viewer" role
  8. Configure custom events in GA4:
     - `form_submit`
     - `email_click`
     - `phone_click`
- Configuration in `.env`:
  ```env
  GA_PROPERTY_ID=123456789
  GA_CREDENTIALS_FILE=path/to/service-account.json
  # OR for production (base64 encoded):
  # GA_CREDENTIALS_JSON_BASE64=eyJ0eXBlIjoi...
  TARGET_WEBSITE=www.lemolegal.sk
  ```

### Google Gemini API
- **API Key**: https://aistudio.google.com/apikey
- **Free Tier**: 15 requests per minute
- **Model**: gemini-2.5-flash
- Configuration in `.env`:
  ```env
  GOOGLE_API_KEY=AIza-your_key_here
  AI_MODEL=gemini-2.5-flash
  ```

### Email (Gmail)
- **Enable 2FA** on Google account
- **App Password**: https://myaccount.google.com/apppasswords
- **Important**: Use app password, NOT regular password
- Configuration in `.env`:
  ```env
  SMTP_HOST=smtp.gmail.com
  SMTP_PORT=587
  SMTP_USE_TLS=true
  SMTP_USERNAME=your.email@gmail.com
  SMTP_PASSWORD=your_app_password
  EMAIL_FROM=your.email@gmail.com
  EMAIL_TO=recipient@example.com
  ```

## Configuration Options

### Scheduling
```env
# Report interval in days (default: 30)
REPORT_INTERVAL_DAYS=30

# Time to send report in 24-hour format (default: 09:00)
REPORT_TIME=09:00

# Timezone (default: UTC)
TIMEZONE=Europe/Bratislava
```

### Logging
```env
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
LOG_ROTATION=10 MB
LOG_RETENTION=30 days
```

### Error Notifications
```env
# Optional: Send error notifications to different email
ERROR_NOTIFICATION_EMAIL=admin@example.com
```

## Troubleshooting

### Check Logs
```powershell
# View recent logs
Get-Content logs/app.log -Tail 50

# Monitor logs in real-time
Get-Content logs/app.log -Wait
```

### Common Issues

#### "Module not found" Error
```powershell
# Reinstall dependencies
uv sync
# or
pip install -e .
```

#### "Authentication failed" - Google Analytics API
- Verify service account JSON file path is correct
- Check service account has "Viewer" role in GA4 property
- Ensure GA4 Property ID is correct (numbers only)
- Verify Google Analytics Data API is enabled in Cloud Console
- Check service account JSON is valid (not corrupted)

#### "Authentication failed" - SMTP (Gmail)
- **Use App Password**, not regular password
- Enable 2-factor authentication first
- Generate app password at https://myaccount.google.com/apppasswords

#### "Invalid API key" - Google Gemini
- Verify key from https://aistudio.google.com/apikey
- Check `.env` file has `GOOGLE_API_KEY=...`
- Ensure no extra spaces or quotes

#### "Rate limit exceeded" - Google Gemini
- Free tier: 15 requests/minute
- Wait 60 seconds or upgrade to paid tier

#### "Configuration error"
- Check all required fields in `.env` are filled
- Verify time format is HH:MM (24-hour)
- Ensure AI model name is correct: `gemini-2.5-flash`

### Test Connections
```powershell
# Verify all external connections
python main.py --test
```

This will check:
- ✓ Google Analytics API connection
- ✓ Google Gemini API connection
- ✓ SMTP email connection

## Production Deployment

### Windows Task Scheduler
1. Open Task Scheduler
2. Create new task
3. Set trigger (e.g., daily at startup)
4. Set action: `python C:\path\to\main.py`
5. Configure to run whether user is logged in or not

### Linux systemd Service
Create `/etc/systemd/system/vercel-analytics.service`:

```ini
[Unit]
Description=Vercel Analytics Report Sender
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/project
ExecStart=/path/to/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable vercel-analytics
sudo systemctl start vercel-analytics
sudo systemctl status vercel-analytics
```

## Security Best Practices

- ✅ Never commit `.env` file to git (already in `.gitignore`)
- ✅ Use app passwords for email (not regular passwords)
- ✅ Rotate API keys periodically
- ✅ Restrict file permissions on `.env` file
- ✅ Use environment variables in production
- ✅ Keep dependencies updated: `uv sync --upgrade`

## Migration Notes

### From OpenAI/Anthropic to Google Gemini
If migrating from older version:
1. Remove `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` from `.env`
2. Add `GOOGLE_API_KEY` to `.env`
3. Update `AI_MODEL=gemini-2.5-flash`
4. Run `uv sync` to update dependencies
5. Test with `python main.py --test`

### Cost Comparison
| Provider | Cost per Report | Free Tier |
|----------|----------------|-----------|
| OpenAI GPT-4 | $0.01-0.02 | No |
| Google Gemini | $0.001 | Yes (15 RPM) |

**Savings**: ~90-95% cost reduction

## Verification Steps

1. **Install dependencies**: `uv sync`
2. **Configure `.env`**: Copy from `.env.example` and fill in credentials
3. **Test connections**: `python main.py --test`
4. **Run first report**: `python main.py --run-once`
5. **Check email**: Verify report received
6. **Review logs**: `Get-Content logs/app.log -Tail 50`
7. **Start scheduler**: `python main.py`

## Support Resources

- **Logs**: `logs/app.log`
- **Memory Bank**: `memory-bank/` directory
- **Configuration Template**: `.env.example`
- **Project Documentation**: `README.md`
