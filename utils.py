"""
Utility functions for Recruitment Email Agent
Includes validation, file handling, user input helpers
"""

import re
import os
import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Callable

def validate_email(email: str) -> bool:
    """Validate email address format"""
    if not email or not isinstance(email, str):
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email.strip()) is not None

def get_user_input(prompt: str, validator: Optional[Callable] = None, 
                  error_msg: str = "Invalid input. Please try again.") -> str:
    """Get user input with validation"""
    while True:
        user_input = input(prompt).strip()
        if validator is None:
            return user_input
        
        if validator(user_input):
            return user_input
        else:
            print(f"❌ {error_msg}")

def confirm_action(message: str) -> bool:
    """Get user confirmation for an action"""
    while True:
        response = input(f"{message} (y/N): ").lower().strip()
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no', '']:
            return False
        else:
            print("Please enter 'y' for yes or 'n' for no.")

def find_resume_files(folder_path: str = "resume") -> List[Path]:
    """Find all resume files in the specified folder"""
    if not os.path.exists(folder_path):
        return []
    
    resume_files = []
    extensions = ['*.pdf', '*.doc', '*.docx']
    
    folder = Path(folder_path)
    for ext in extensions:
        resume_files.extend(folder.glob(ext))
    
    # Sort by modification time (newest first)
    resume_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    
    return resume_files

def select_resume_file(resume_files: List[Path]) -> Optional[Path]:
    """Let user select a resume file from available options"""
    if not resume_files:
        return None
    
    if len(resume_files) == 1:
        return resume_files[0]
    
    print(f"\n📄 Found {len(resume_files)} resume files:")
    print("-" * 40)
    
    for i, file in enumerate(resume_files, 1):
        file_size = file.stat().st_size / 1024  # Size in KB
        mod_time = datetime.fromtimestamp(file.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
        print(f"{i}. {file.name}")
        print(f"   📏 Size: {file_size:.1f} KB  📅 Modified: {mod_time}")
    
    print("-" * 40)
    
    while True:
        try:
            choice = input(f"Select resume file (1-{len(resume_files)}): ").strip()
            if choice == "":
                print("❌ Please make a selection.")
                continue
            
            index = int(choice) - 1
            if 0 <= index < len(resume_files):
                return resume_files[index]
            else:
                print(f"❌ Please enter a number between 1 and {len(resume_files)}.")
        except ValueError:
            print("❌ Please enter a valid number.")

def create_folder_if_not_exists(folder_path: str) -> bool:
    """Create folder if it doesn't exist"""
    try:
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            print(f"📁 Created folder: {folder_path}")
        return True
    except Exception as e:
        print(f"❌ Failed to create folder {folder_path}: {e}")
        return False

def log_email_activity(log_file: str, recipient_email: str, company_name: Optional[str], 
                      subject: str, success: bool, error_msg: Optional[str] = None) -> None:
    """Log email sending activity"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "recipient": recipient_email,
        "company": company_name or "Not specified",
        "subject": subject,
        "success": success,
        "error": error_msg
    }
    
    logs = []
    if os.path.exists(log_file):
        try:
            with open(log_file, 'r') as f:
                logs = json.load(f)
        except json.JSONDecodeError:
            print("⚠️  Log file corrupted. Starting fresh log.")
            logs = []
    
    logs.append(log_entry)
    
    try:
        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)
    except Exception as e:
        print(f"⚠️  Failed to write to log file: {e}")

def show_recent_emails(log_file: str, count: int = 5) -> None:
    """Display recent email activity"""
    if not os.path.exists(log_file):
        print("📪 No email history found.")
        return
    
    try:
        with open(log_file, 'r') as f:
            logs = json.load(f)
        
        if not logs:
            print("📪 No emails logged yet.")
            return
        
        recent_logs = logs[-count:]
        
        print(f"\n📊 Last {len(recent_logs)} emails:")
        print("-" * 50)
        
        for log in reversed(recent_logs):
            timestamp = datetime.fromisoformat(log['timestamp']).strftime("%Y-%m-%d %H:%M")
            status = "✅ Sent" if log['success'] else "❌ Failed"
            
            print(f"{timestamp} | {status}")
            print(f"   📧 To: {log['recipient']}")
            if log['company'] != "Not specified":
                print(f"   🏢 Company: {log['company']}")
            print(f"   📝 Subject: {log['subject']}")
            if not log['success'] and log.get('error'):
                print(f"   ⚠️  Error: {log['error']}")
            print()
            
    except Exception as e:
        print(f"❌ Failed to read log file: {e}")

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

def clean_string_for_filename(text: str) -> str:
    """Clean string to be safe for filename use"""
    # Remove or replace invalid filename characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        text = text.replace(char, '_')
    
    # Limit length and strip whitespace
    return text.strip()[:50]