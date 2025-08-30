#!/usr/bin/env python3
"""
Recruitment Email Agent - Main Entry Point
"""

from email_agent import RecruitmentEmailAgent
from config_manager import ConfigManager
from utils import validate_email, get_user_input, confirm_action
import sys
import os

def main():
    """Main execution flow with user prompts"""
    print("🤖 Recruitment Email Agent")
    print("=" * 40)
    print("Send personalized recruitment emails with your resume automatically!")
    
    try:
        # Initialize components
        config_manager = ConfigManager()
        email_agent = RecruitmentEmailAgent(config_manager)
        
        # Load or setup configuration from files
        print("\n📋 Loading configuration...")
        config = config_manager.load_config()
        
        if not config:
            print("❌ Configuration setup failed.")
            print("📋 Please check setup_details.txt and template files.")
            print("📖 See FILE_COPYING_GUIDE.md for help.")
            return
        
        # Show current config
        config_manager.show_current_config()
        
        # Get user inputs with prompts for this specific email
        print("\n📝 Enter email details:")
        recipient_email = get_user_input(
            "📬 Recipient email: ", 
            validator=validate_email,
            error_msg="Invalid email format. Please try again."
        )
        
        recipient_name = input("👤 Recipient name (optional, press Enter to skip): ").strip()
        if not recipient_name:
            recipient_name = None
        
        company_name = input("🏢 Company name (optional, press Enter to skip): ").strip()
        if not company_name:
            company_name = None
            
        # Show template selection if both templates exist
        template_choice = None
        if os.path.exists("template_person_only.txt") and os.path.exists("template_person_company.txt"):
            print("\n📝 Template Options:")
            print("1. Person only template (no company name)")
            print("2. Person + Company template (includes company)")
            
            while True:
                choice = input("Choose template (1 or 2, or Enter for default): ").strip()
                if choice == "1":
                    template_choice = "person_only"
                    break
                elif choice == "2":
                    template_choice = "person_company"
                    break
                elif choice == "":
                    template_choice = config.get("template_preference", "person_company")
                    break
                else:
                    print("Please enter 1, 2, or press Enter for default.")
        
        bcc_email = input("📧 BCC email (optional, press Enter to skip): ").strip()
        if bcc_email:
            if not validate_email(bcc_email):
                print("⚠️  Invalid BCC email format, skipping BCC.")
                bcc_email = None
        else:
            bcc_email = None
        
        # Ask for custom subject line
        custom_subject = input("📝 Email subject (optional, press Enter for AI-generated): ").strip()
        if not custom_subject:
            custom_subject = None
        
        # Get resume file
        print("\n📄 Checking for resume files...")
        resume_file = email_agent.get_resume_file()
        if not resume_file:
            print("❌ Cannot proceed without resume file.")
            print("📁 Please add your resume (PDF/Word) to the 'resume' folder.")
            return
        
        print(f"✅ Found resume: {resume_file.name}")
        
        # Update template if different choice made
        if template_choice and template_choice != config.get("template_preference"):
            new_template = config_manager.read_email_template(template_choice)
            if new_template:
                config["email_template"] = new_template
                config["template_preference"] = template_choice
                print(f"📝 Using {template_choice} template for this email")
        
        # Show summary and confirm
        print(f"\n📧 Email Summary:")
        print(f"   📬 To: {recipient_email}")
        if recipient_name:
            print(f"   👤 Name: {recipient_name}")
        else:
            print(f"   👤 Name: Hiring Manager (default)")
        if company_name:
            print(f"   🏢 Company: {company_name}")
        else:
            print(f"   🏢 Company: [Not specified]")
        if bcc_email:
            print(f"   📧 BCC: {bcc_email}")
        if custom_subject:
            print(f"   📝 Subject: {custom_subject}")
        else:
            print(f"   📝 Subject: AI-generated")
        print(f"   📄 Resume: {resume_file.name}")
        print(f"   📝 Template: {config.get('template_preference', 'person_company')}")
        
        # Final confirmation
        if not confirm_action("Send this email?"):
            print("❌ Email cancelled by user.")
            return
        
        # Send email
        print("\n🚀 Generating subject and sending email...")
        success = email_agent.send_recruitment_email(
            recipient_email=recipient_email,
            recipient_name=recipient_name,
            company_name=company_name,
            bcc_email=bcc_email,
            resume_file=resume_file,
            custom_subject=custom_subject
        )
        
        if success:
            print("\n✅ Email sent successfully! 🎉")
            print("📊 Check 'sent_emails.json' for delivery log.")
        else:
            print("\n❌ Failed to send email. Check logs for details.")
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Process interrupted by user. Exiting...")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("🐛 Please check your configuration and try again.")

if __name__ == "__main__":
    main()