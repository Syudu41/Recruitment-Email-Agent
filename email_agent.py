"""
Recruitment Email Agent - Core Email Functionality
Handles email composition, sending, and file management
"""

import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from typing import Optional

from config_manager import ConfigManager
from ollama_client import OllamaClient
from utils import (
    find_resume_files, select_resume_file, create_folder_if_not_exists,
    log_email_activity, format_file_size
)

class RecruitmentEmailAgent:
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.ollama_client = OllamaClient()
        self.resume_folder = "resume"
        self.log_file = "sent_emails.json"
        
        # Ensure resume folder exists
        create_folder_if_not_exists(self.resume_folder)
    
    def get_resume_file(self) -> Optional[Path]:
        """Find and select resume file"""
        resume_files = find_resume_files(self.resume_folder)
        
        if not resume_files:
            print(f"❌ No resume files found in '{self.resume_folder}' folder!")
            print(f"📁 Please add your resume (PDF/Word documents) to the '{self.resume_folder}' folder.")
            print("📋 Supported formats: PDF, DOC, DOCX")
            return None
        
        return select_resume_file(resume_files)
    
    def _create_email_message(self, recipient_email: str, recipient_name: Optional[str],
                            company_name: Optional[str], bcc_email: Optional[str],
                            subject: str, body: str, resume_file: Path) -> MIMEMultipart:
        """Create email message with all components"""
        config = self.config_manager.get_config()
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = f"{config['sender_name']} <{config['sender_email']}>"
        msg['To'] = recipient_email
        msg['Subject'] = subject
        
        if bcc_email:
            msg['Bcc'] = bcc_email
        
        # Attach email body
        msg.attach(MIMEText(body, 'plain'))
        
        # Attach resume
        try:
            with open(resume_file, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {resume_file.name}'
            )
            msg.attach(part)
            
            print(f"📎 Attached: {resume_file.name} ({format_file_size(resume_file.stat().st_size)})")
            
        except Exception as e:
            print(f"❌ Failed to attach resume: {e}")
            raise
        
        return msg
    
    def _send_via_smtp(self, message: MIMEMultipart, recipients: list) -> bool:
        """Send email via SMTP"""
        config = self.config_manager.get_config()
        
        try:
            print("🔗 Connecting to Gmail SMTP...")
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            
            print("🔐 Authenticating...")
            server.login(config['sender_email'], config['sender_password'])
            
            print("📤 Sending email...")
            server.send_message(message, to_addrs=recipients)
            server.quit()
            
            return True
            
        except smtplib.SMTPAuthenticationError:
            print("❌ Gmail authentication failed!")
            print("🔧 Check your Gmail App Password (not regular password)")
            print("📖 Help: https://support.google.com/accounts/answer/185833")
            return False
            
        except smtplib.SMTPRecipientsRefused:
            print("❌ Recipient email address rejected by server!")
            return False
            
        except smtplib.SMTPServerDisconnected:
            print("❌ SMTP server disconnected unexpectedly!")
            return False
            
        except Exception as e:
            print(f"❌ SMTP error: {e}")
            return False
    
    def send_recruitment_email(self, recipient_email: str, recipient_name: Optional[str],
                             company_name: Optional[str], bcc_email: Optional[str],
                             resume_file: Path, custom_subject: Optional[str] = None) -> bool:
        """Main method to send recruitment email"""
        
        config = self.config_manager.get_config()
        if not config:
            print("❌ No configuration found!")
            return False
        
        try:
            # Use custom subject or generate with AI
            if custom_subject:
                print(f"📝 Using custom subject: {custom_subject}")
                subject = custom_subject
            else:
                print("🎯 Generating personalized subject line...")
                subject = self.ollama_client.generate_subject_line(
                    recipient_name, company_name, config['sender_name']
                )
            
            # Prepare email body with template handling
            print("✍️  Preparing email content...")
            
            # Handle both person_only and person_company templates
            template = config['email_template']
            
            # Set defaults for missing values
            display_name = recipient_name or "Hiring Manager"
            display_company = company_name or "your organization"
            
            # For person_only template, don't include company references
            if config.get('template_preference') == 'person_only':
                # Only use name, no company mentions
                email_body = template.format(
                    name=display_name,
                    sender_name=config['sender_name']
                )
            else:
                # For person_company template, include company
                # If no company provided, use generic "your organization"
                email_body = template.format(
                    name=display_name,
                    company=display_company,
                    sender_name=config['sender_name']
                )
            
            # Create email message
            print("📧 Composing email...")
            message = self._create_email_message(
                recipient_email, recipient_name, company_name, 
                bcc_email, subject, email_body, resume_file
            )
            
            # Prepare recipient list
            recipients = [recipient_email]
            if bcc_email:
                recipients.append(bcc_email)
                print(f"📧 BCC: {bcc_email}")
            
            # Send email
            success = self._send_via_smtp(message, recipients)
            
            # Log the attempt
            log_email_activity(
                self.log_file, recipient_email, company_name, 
                subject, success, None if success else "SMTP sending failed"
            )
            
            if success:
                print(f"✅ Email sent successfully!")
                print(f"📝 Subject: {subject}")
                print(f"📧 To: {recipient_email}")
                if bcc_email:
                    print(f"📧 BCC: {bcc_email}")
                print(f"📎 Attachment: {resume_file.name}")
            
            return success
            
        except FileNotFoundError:
            error_msg = f"Resume file not found: {resume_file}"
            print(f"❌ {error_msg}")
            log_email_activity(
                self.log_file, recipient_email, company_name,
                "Failed - File Not Found", False, error_msg
            )
            return False
            
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            print(f"❌ {error_msg}")
            log_email_activity(
                self.log_file, recipient_email, company_name,
                "Failed - Unexpected Error", False, error_msg
            )
            return False
    
    def test_email_setup(self) -> bool:
        """Test email configuration and connection"""
        config = self.config_manager.get_config()
        if not config:
            print("❌ No email configuration found!")
            return False
        
        print("🧪 Testing email setup...")
        
        try:
            # Test SMTP connection
            print("🔗 Testing Gmail SMTP connection...")
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(config['sender_email'], config['sender_password'])
            server.quit()
            
            print("✅ Email configuration is working!")
            return True
            
        except smtplib.SMTPAuthenticationError:
            print("❌ Authentication failed!")
            print("🔧 Check your Gmail App Password")
            return False
            
        except Exception as e:
            print(f"❌ Connection test failed: {e}")
            return False
    
    def test_ollama_setup(self) -> bool:
        """Test Ollama connection and model availability"""
        print("🤖 Testing Ollama setup...")
        status = self.ollama_client.test_connection()
        
        print(f"   Ollama Service: {'✅ Running' if status['ollama_running'] else '❌ Not Running'}")
        print(f"   Model Available: {'✅ Ready' if status['model_available'] else '❌ Not Found'}")
        
        if status['available_models']:
            print(f"   Available Models: {', '.join(status['available_models'][:3])}")
        
        print(f"   Status: {status['message']}")
        
        return status['ollama_running'] and status['model_available']
    
    def show_system_status(self) -> None:
        """Display complete system status"""
        print("\n" + "=" * 50)
        print("🔍 SYSTEM STATUS")
        print("=" * 50)
        
        # Configuration status
        config = self.config_manager.get_config()
        print(f"📋 Configuration: {'✅ Loaded' if config else '❌ Missing'}")
        if config:
            self.config_manager.show_current_config()
        
        # Resume files status
        resume_files = find_resume_files(self.resume_folder)
        print(f"\n📄 Resume Files: {len(resume_files)} found")
        if resume_files:
            for file in resume_files[:3]:  # Show first 3
                size = format_file_size(file.stat().st_size)
                print(f"   📎 {file.name} ({size})")
        
        # Email setup status
        print(f"\n📧 Email Setup:", end=" ")
        if config:
            email_working = self.test_email_setup()
        else:
            print("❌ Not configured")
            
        # Ollama status
        print(f"\n🤖 AI Status:")
        self.test_ollama_setup()
        
        print("\n" + "=" * 50)