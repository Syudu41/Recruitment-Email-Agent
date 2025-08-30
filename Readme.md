# 🤖 Recruitment Email Agent

Automate sending personalized recruitment emails with AI-generated subject lines and resume attachments.

## ✨ Features

- **Interactive Setup**: Guided first-time configuration
- **AI Subject Generation**: Uses local Ollama for personalized subject lines  
- **Resume Auto-Detection**: Finds and selects resume files automatically
- **Email Validation**: Prevents sending to invalid addresses
- **BCC Support**: Copy yourself or others on sent emails
- **Activity Logging**: Track all sent emails with timestamps
- **Robust Error Handling**: Graceful fallbacks when services are unavailable

## 📁 Project Structure

```
recruitment-agent/
├── main.py              # Main entry point with user prompts
├── email_agent.py       # Core email functionality
├── config_manager.py    # Configuration management  
├── ollama_client.py     # AI subject generation
├── utils.py            # Utility functions
├── requirements.txt     # Python dependencies
├── resume/             # Your resume files (PDF/Word)
│   └── your_resume.pdf
├── email_config.json   # Auto-generated configuration
└── sent_emails.json    # Email activity log
```

## 🚀 Quick Start

### 1. Prerequisites

**Install Ollama:**
```bash
# Download from https://ollama.ai
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
ollama serve

# Pull the AI model
ollama pull mistral
```

**Gmail App Password:**
- Enable 2-Factor Authentication on Gmail
- Generate App Password: [Google Support Guide](https://support.google.com/accounts/answer/185833)

### 2. Setup Project

```bash
# Clone/download all Python files
# Install dependencies
pip install -r requirements.txt

# Create resume folder and add your resume
mkdir resume
# Copy your resume.pdf to the resume/ folder
```

### 3. Run the Agent

```bash
python main.py
```

The agent will guide you through:
1. **First-time setup** (Gmail credentials, email template)
2. **Interactive prompts** for each email
3. **AI-powered subject generation** 
4. **Confirmation before sending**

## 📧 Sample Email Flow

```
🤖 Recruitment Email Agent
========================================
📋 Checking configuration...
✅ Configuration loaded from email_config.json

📝 Enter email details:
Recipient email: recruiter@company.com
Recipient name (optional): Sarah Johnson  
Company name (optional): TechCorp
BCC email (optional): me@gmail.com

📄 Found resume: John_Smith_Resume.pdf

📧 Email Summary:
   📬 To: recruiter@company.com
   👤 Name: Sarah Johnson
   🏢 Company: TechCorp  
   📧 BCC: me@gmail.com
   📄 Resume: John_Smith_Resume.pdf

Send this email? (y/N): y

🚀 Generating subject and sending email...
🤖 Generating subject line with mistral...
✨ AI generated: Senior Developer Application - John Smith
✅ Email sent successfully! 🎉
```

## 🛠️ Configuration Files

### email_config.json
```json
{
  "sender_email": "your.email@gmail.com",
  "sender_password": "your_app_password",
  "sender_name": "Your Name",
  "email_template": "Dear {name},\n\nI am writing to express interest in opportunities at {company}...",
  "setup_date": "2025-01-01T12:00:00"
}
```

### Email Template Variables
- `{name}` - Recipient name (defaults to "Hiring Manager")
- `{company}` - Company name (defaults to "your company")

## 🔧 Troubleshooting

### Ollama Issues
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Install mistral model if missing
ollama pull mistral

# Alternative models to try
ollama pull llama2
ollama pull codellama
```

### Gmail Authentication Errors
- Verify 2FA is enabled on Gmail
- Generate new App Password (not regular password)
- Check email/password in `email_config.json`

### Resume File Issues  
- Supported formats: PDF, DOC, DOCX
- Place files in `resume/` folder
- Check file permissions

## 📊 Monitoring & Logs

### View Recent Activity
The agent automatically logs all email attempts to `sent_emails.json`:

```json
[
  {
    "timestamp": "2025-08-29T14:30:00",
    "recipient": "recruiter@company.com",
    "company": "TechCorp",
    "subject": "Senior Developer Application - John Smith",
    "success": true,
    "error": null
  }
]
```

### System Status Check
Add this to `main.py` to check system health:
```python
# Add after agent initialization
agent.show_system_status()
```

## 🔄 Advanced Usage

### Custom AI Models
Edit `ollama_client.py` line 10:
```python
def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama2"):
```

### Multiple Resume Files
The agent will automatically detect multiple resumes and prompt you to choose:
```
📄 Found 3 resume files:
1. John_Smith_Resume_2024.pdf (245.3 KB  📅 2024-08-15 10:30)
2. John_Smith_Resume_Technical.pdf (198.7 KB  📅 2024-08-10 15:45)  
3. John_Smith_Resume_Manager.pdf (203.1 KB  📅 2024-08-05 09:20)
Select resume file (1-3): 1
```

### Reset Configuration
Delete `email_config.json` to trigger first-time setup again.

## 🆘 Support

If you encounter issues:

1. **Check system status**: Run the agent and look for red ❌ indicators
2. **Verify prerequisites**: Ollama running, Gmail App Password set
3. **Check logs**: Look at `sent_emails.json` for error details
4. **Test components**: Each module can be imported and tested individually

## 🔒 Security Notes

- Gmail App Passwords are stored locally in `email_config.json`
- No data is sent to external services except Gmail SMTP
- Ollama runs locally - no API keys needed
- Email logs contain recipient addresses - secure your system appropriately