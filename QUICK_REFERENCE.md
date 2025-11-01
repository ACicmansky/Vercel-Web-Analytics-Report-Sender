# Quick Reference Card

## Installation
```powershell
# Using uv (recommended)
uv sync

# Or using pip
pip install -e .
```

## Configuration
```powershell
Copy-Item .env.example .env
# Edit .env with your credentials
```

## Commands

| Command | Purpose |
|---------|---------|
| `python main.py --test` | Test all connections |
| `python main.py --run-once` | Run report once |
| `python main.py` | Start scheduler |
| `python main.py --run-immediately` | Run now + schedule |
| `python main.py --log-level DEBUG` | Enable debug logging |

## Required Credentials

### Vercel
- API Token: https://vercel.com/account/tokens
- Team ID: From Vercel dashboard
- Project ID: From Vercel dashboard

### Google Gemini
- API Key: https://aistudio.google.com/apikey
- Free tier available

### Email (Gmail)
- Enable 2FA
- Create App Password: https://myaccount.google.com/apppasswords
- Use app password in SMTP_PASSWORD

## Key Files

| File | Purpose |
|------|---------|
| `.env` | Your credentials (never commit!) |
| `main.py` | Application entry point |
| `logs/app.log` | Application logs |
| `README.md` | Full documentation |
| `SETUP_GUIDE.md` | Setup instructions |

## Troubleshooting

### Check Logs
```powershell
Get-Content logs/app.log -Tail 50
```

### Test Connections
```powershell
python main.py --test
```

### Common Fixes

**Module not found:**
```powershell
pip install -e .
```

**SMTP auth failed (Gmail):**
- Use App Password, not regular password
- Enable 2FA first

**Vercel API error:**
- Verify API token
- Check team/project IDs

## Configuration Quick Reference

```env
# Vercel
VERCEL_API_TOKEN=your_token
TARGET_WEBSITE=www.lemolegal.sk

# AI
GOOGLE_API_KEY=AIza-your_key
AI_MODEL=gemini-2.0-flash-exp

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your@email.com
SMTP_PASSWORD=your_app_password
EMAIL_TO=recipient@email.com

# Schedule
REPORT_INTERVAL_DAYS=30
REPORT_TIME=09:00
TIMEZONE=Europe/Bratislava
```

## Project Structure

```
src/
├── config.py          # Configuration
├── scheduler.py       # Scheduling
├── vercel/           # Vercel API
├── processing/       # Data analysis
├── ai/               # AI summaries
├── email/            # Email delivery
└── utils/            # Logging, retry
```

## Support

1. Check `logs/app.log`
2. Review `SETUP_GUIDE.md`
3. Read `README.md`
4. Check `memory-bank/` docs

## Status

✅ Core implementation complete  
⏳ Testing with real APIs pending  
⏳ Production deployment pending  

---

**Ready to start?** Run `python main.py --test` to verify your setup!
