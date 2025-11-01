# Setup Guide

Quick start guide for setting up and running the Vercel Web Analytics Report Sender.

## Prerequisites

- Python 3.11 or higher
- uv package manager (recommended) or pip
- Vercel account with API access
- Google Gemini API account
- Email account with SMTP access (Gmail recommended)

## Step-by-Step Setup

### 1. Install Dependencies

```powershell
# Using uv (recommended)
uv sync

# Or using pip
pip install -e .
```

### 2. Configure Environment Variables

Copy the example environment file:
```powershell
Copy-Item .env.example .env
```

Edit `.env` and fill in your credentials:

#### Vercel Configuration
```env
VERCEL_API_TOKEN=your_token_here
VERCEL_TEAM_ID=your_team_id
VERCEL_PROJECT_ID=your_project_id
TARGET_WEBSITE=www.lemolegal.sk
```

**How to get Vercel credentials:**
1. Go to https://vercel.com/account/tokens
2. Create a new token with read access
3. Find your team ID and project ID in the Vercel dashboard

#### Google Gemini Configuration
```env
GOOGLE_API_KEY=AIza-your_key_here
AI_MODEL=gemini-2.5-flash
```

**How to get Google Gemini API key:**
1. Go to https://aistudio.google.com/apikey
2. Create a new API key
3. Free tier available with generous limits

#### Email Configuration (Gmail Example)
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_TLS=true
SMTP_USERNAME=your.email@gmail.com
SMTP_PASSWORD=your_app_password
EMAIL_FROM=your.email@gmail.com
EMAIL_TO=recipient@example.com
```

**How to set up Gmail:**
1. Enable 2-factor authentication on your Google account
2. Go to https://myaccount.google.com/apppasswords
3. Generate an "App Password" for "Mail"
4. Use this app password (not your regular password)

### 3. Test Connections

Before running the full application, test all connections:

```powershell
python main.py --test
```

This will verify:
- ✓ Vercel API connection
- ✓ OpenAI API connection
- ✓ SMTP email connection

### 4. Run Your First Report

Generate a report immediately (without scheduling):

```powershell
python main.py --run-once
```

This will:
1. Fetch analytics from Vercel
2. Process the data
3. Generate AI summary
4. Send email report

### 5. Start Scheduled Reporting

Run the application with scheduling enabled:

```powershell
# Start scheduler (runs at configured time daily)
python main.py

# Or run immediately, then start scheduler
python main.py --run-immediately
```

## Configuration Options

### Scheduling

Control when reports are generated:

```env
# Report interval in days (default: 30)
REPORT_INTERVAL_DAYS=30

# Time to send report in 24-hour format (default: 09:00)
REPORT_TIME=09:00

# Timezone (default: UTC)
TIMEZONE=Europe/Bratislava
```

### Logging

Configure logging behavior:

```env
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
LOG_ROTATION=10 MB
LOG_RETENTION=30 days
```

### Error Notifications

Optionally send error notifications to a different email:

```env
ERROR_NOTIFICATION_EMAIL=admin@example.com
```

## Command Line Options

```powershell
# Test connections only
python main.py --test

# Run report once and exit
python main.py --run-once

# Run immediately, then start scheduler
python main.py --run-immediately

# Set log level
python main.py --log-level DEBUG
```

## Troubleshooting

### "Authentication failed" - Vercel API

- Verify your API token is correct
- Check token has required permissions
- Ensure team ID and project ID are correct

### "Authentication failed" - SMTP

**For Gmail:**
- Use App Password, not regular password
- Enable 2-factor authentication first
- Check "Less secure app access" if needed

**For other providers:**
- Verify SMTP host and port
- Check if TLS/SSL is required
- Confirm username and password

### "Module not found" errors

```powershell
# Reinstall dependencies
pip install -e .
```

### "Configuration error"

- Check all required fields in `.env` are filled
- Verify time format is HH:MM (24-hour)
- Ensure AI model name is correct

## Verifying Setup

### Check Logs

Logs are stored in `logs/app.log`:

```powershell
# View recent logs (PowerShell)
Get-Content logs/app.log -Tail 50

# Monitor logs in real-time
Get-Content logs/app.log -Wait
```

### Test Email Delivery

The `--run-once` command is perfect for testing:

```powershell
python main.py --run-once
```

Check your email inbox for the report!

## Next Steps

Once setup is complete:

1. **Review the first report** - Check email formatting and content
2. **Adjust scheduling** - Modify `REPORT_INTERVAL_DAYS` if needed
3. **Monitor logs** - Watch for any errors or warnings
4. **Set up monitoring** - Consider system service or task scheduler

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
```

## Support

For issues:
1. Check logs in `logs/app.log`
2. Review this setup guide
3. Check README.md for more details
4. Verify all credentials are correct

## Security Best Practices

- ✅ Never commit `.env` file to git
- ✅ Use app passwords for email (not regular passwords)
- ✅ Rotate API keys periodically
- ✅ Restrict file permissions on `.env`
- ✅ Use environment variables in production

---

**Ready to go!** 🚀

Your Vercel Web Analytics Report Sender is now configured and ready to deliver automated insights.
