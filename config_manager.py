"""
Configuration Manager for Recruitment Email Agent
Handles email setup, template management, and persistent configuration
"""

import json
import os
from typing import Dict, Optional

class ConfigManager:
    def __init__(self, config_file: str = "email_config.json"):
        self.config_file = config_file
        self.config = None
    
    def load_config(self) -> Optional[Dict]:
        """Load existing configuration or trigger first-time setup"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
                print(f"✅ Configuration loaded from {self.config_file}")
                return self.config
            except json.JSONDecodeError:
                print(f"⚠️  Corrupted config file. Running first-time setup...")
                return self.setup_first_time()
        else:
            print("📧 First time setup detected...")
            return self.setup_first_time()
    
    def read_setup_details(self) -> Optional[Dict]:
        """Read setup details from setup_details.txt file"""
        setup_file = "setup_details.txt"
        
        if not os.path.exists(setup_file):
            print(f"❌ {setup_file} not found!")
            print("📁 Please create and fill out setup_details.txt with your Gmail credentials.")
            print("📖 See setup_details.txt template in the repository.")
            return None
        
        try:
            details = {}
            with open(setup_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        details[key.strip()] = value.strip()
            
            # Check required fields
            required_fields = ['GMAIL_EMAIL', 'GMAIL_APP_PASSWORD', 'SENDER_NAME']
            missing_fields = [field for field in required_fields if not details.get(field)]
            
            if missing_fields:
                print(f"❌ Missing required fields in {setup_file}: {', '.join(missing_fields)}")
                return None
            
            return details
            
        except Exception as e:
            print(f"❌ Error reading {setup_file}: {e}")
            return None
    
    def read_email_template(self, template_preference: str = "person_company") -> Optional[str]:
        """Read email template from template files"""
        template_files = {
            "person_only": "template_person_only.txt",
            "person_company": "template_person_company.txt"
        }
        
        template_file = template_files.get(template_preference, "template_person_company.txt")
        
        if not os.path.exists(template_file):
            print(f"❌ Template file {template_file} not found!")
            print("📁 Please create the template files:")
            for key, file in template_files.items():
                print(f"   - {file} (for {key} emails)")
            return None
        
        try:
            with open(template_file, 'r') as f:
                template = f.read().strip()
            
            if not template:
                print(f"❌ Template file {template_file} is empty!")
                return None
            
            return template
            
        except Exception as e:
            print(f"❌ Error reading template file {template_file}: {e}")
            return None

    def setup_first_time(self) -> Optional[Dict]:
        """Setup configuration from files"""
        print("\n" + "=" * 50)
        print("🔧 FIRST-TIME SETUP FROM FILES")
        print("=" * 50)
        
        # Read setup details
        print("📋 Reading setup details...")
        details = self.read_setup_details()
        if not details:
            return None
        
        # Read email template
        template_preference = details.get('PREFERRED_TEMPLATE', 'person_company')
        print(f"📝 Loading email template ({template_preference})...")
        email_template = self.read_email_template(template_preference)
        if not email_template:
            return None
        
        # Create configuration from file details
        config = {
            "sender_email": details['GMAIL_EMAIL'],
            "sender_password": details['GMAIL_APP_PASSWORD'], 
            "sender_name": details['SENDER_NAME'],
            "email_template": email_template,
            "template_preference": template_preference,
            "setup_date": str(__import__('datetime').datetime.now())
        }
        
        # Save configuration
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            print(f"\n✅ Configuration loaded successfully!")
            print(f"📧 Email: {details['GMAIL_EMAIL']}")
            print(f"👤 Name: {details['SENDER_NAME']}")
            print(f"📝 Template: {template_preference}")
            print(f"📁 Config saved to: {self.config_file}")
            
            self.config = config
            return config
            
        except Exception as e:
            print(f"❌ Failed to save configuration: {e}")
            return None
    
    def get_config(self) -> Optional[Dict]:
        """Get current configuration"""
        return self.config
    
    def update_template(self, new_template: str) -> bool:
        """Update email template in configuration"""
        if not self.config:
            print("❌ No configuration loaded.")
            return False
        
        try:
            self.config["email_template"] = new_template
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            print("✅ Email template updated successfully!")
            return True
        except Exception as e:
            print(f"❌ Failed to update template: {e}")
            return False
    
    def show_current_config(self) -> None:
        """Display current configuration (without passwords)"""
        if not self.config:
            print("❌ No configuration loaded.")
            return
        
        print("\n📋 Current Configuration:")
        print(f"   📧 Email: {self.config.get('sender_email', 'Not set')}")
        print(f"   👤 Name: {self.config.get('sender_name', 'Not set')}")
        print(f"   📝 Template: {'Set' if self.config.get('email_template') else 'Not set'}")
        
        if self.config.get('setup_date'):
            print(f"   📅 Setup: {self.config['setup_date'][:19]}")
    
    def reset_config(self) -> bool:
        """Reset configuration (delete config file)"""
        try:
            if os.path.exists(self.config_file):
                os.remove(self.config_file)
                self.config = None
                print(f"✅ Configuration reset. Run again for first-time setup.")
                return True
            else:
                print("⚠️  No configuration file found.")
                return False
        except Exception as e:
            print(f"❌ Failed to reset configuration: {e}")
            return False