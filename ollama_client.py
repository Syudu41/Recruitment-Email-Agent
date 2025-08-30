"""
Ollama Client for AI-powered subject line generation
Handles communication with local Ollama instance
"""

import requests
import json
from typing import Optional

class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "mistral"):
        self.base_url = base_url
        self.model = model
        self.generate_url = f"{base_url}/api/generate"
        self.models_url = f"{base_url}/api/tags"
    
    def is_ollama_running(self) -> bool:
        """Check if Ollama service is running"""
        try:
            response = requests.get(self.models_url, timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def is_model_available(self, model_name: str = None) -> bool:
        """Check if specified model is available"""
        model_name = model_name or self.model
        
        try:
            response = requests.get(self.models_url, timeout=5)
            if response.status_code == 200:
                models_data = response.json()
                available_models = [model['name'].split(':')[0] for model in models_data.get('models', [])]
                return model_name in available_models
            return False
        except requests.exceptions.RequestException:
            return False
    
    def get_available_models(self) -> list:
        """Get list of available models"""
        try:
            response = requests.get(self.models_url, timeout=5)
            if response.status_code == 200:
                models_data = response.json()
                return [model['name'] for model in models_data.get('models', [])]
            return []
        except requests.exceptions.RequestException:
            return []
    
    def generate_subject_line(self, recipient_name: Optional[str], 
                            company_name: Optional[str], 
                            sender_name: str) -> str:
        """Generate professional email subject line using AI"""
        
        # Check if Ollama is running
        if not self.is_ollama_running():
            print("⚠️  Ollama service not running. Using default subject.")
            return self._default_subject(sender_name, company_name)
        
        # Check if model is available
        if not self.is_model_available():
            print(f"⚠️  Model '{self.model}' not found. Using default subject.")
            available = self.get_available_models()
            if available:
                print(f"💡 Available models: {', '.join(available[:3])}")
                print(f"💡 Install with: ollama pull {self.model}")
            return self._default_subject(sender_name, company_name)
        
        # Create prompt for subject generation
        prompt = self._create_subject_prompt(recipient_name, company_name, sender_name)
        
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_tokens": 50
                }
            }
            
            print(f"🤖 Generating subject line with {self.model}...")
            response = requests.post(self.generate_url, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                subject = result.get('response', '').strip()
                
                # Clean and validate the generated subject
                subject = self._clean_subject(subject)
                
                if self._is_valid_subject(subject):
                    print(f"✨ AI generated: {subject}")
                    return subject
                else:
                    print("⚠️  Generated subject seems invalid. Using default.")
                    return self._default_subject(sender_name, company_name)
            
            else:
                print(f"⚠️  Ollama API error ({response.status_code}). Using default subject.")
                return self._default_subject(sender_name, company_name)
        
        except requests.exceptions.Timeout:
            print("⚠️  Ollama request timeout. Using default subject.")
            return self._default_subject(sender_name, company_name)
        
        except requests.exceptions.RequestException as e:
            print(f"⚠️  Ollama request failed: {e}. Using default subject.")
            return self._default_subject(sender_name, company_name)
        
        except Exception as e:
            print(f"⚠️  Unexpected error: {e}. Using default subject.")
            return self._default_subject(sender_name, company_name)
    
    def _create_subject_prompt(self, recipient_name: Optional[str], 
                             company_name: Optional[str], 
                             sender_name: str) -> str:
        """Create prompt for subject line generation"""
        
        context_parts = []
        if company_name and company_name != "your organization":
            context_parts.append(f"Company: {company_name}")
        if recipient_name and recipient_name != "Hiring Manager":
            context_parts.append(f"Recipient: {recipient_name}")
        context_parts.append(f"Applicant: {sender_name}")
        
        context = "\n".join(context_parts)
        
        prompt = f"""Generate a professional email subject line for a job application. 

Context:
{context}

Requirements:
- Professional and engaging
- 50 characters or less
- No quotes or special formatting
- Include applicant name
- Make it stand out in an inbox

Examples of good subjects:
- "Software Engineer Application - John Smith"
- "Experienced Developer Seeking Opportunities - Jane Doe"
- "Application for Python Developer Role - John Smith"
- "Senior Engineer Position - John Smith"
{"- Application for Position at " + company_name + " - John Smith" if company_name and company_name != "your organization" else ""}

Generate only the subject line, nothing else:"""
        
        return prompt
    
    def _clean_subject(self, subject: str) -> str:
        """Clean and format the generated subject line"""
        if not subject:
            return ""
        
        # Remove common unwanted elements
        subject = subject.strip()
        subject = subject.replace('"', '').replace("'", '')
        subject = subject.replace('\n', ' ').replace('\r', ' ')
        
        # Remove "Subject:" prefix if present
        if subject.lower().startswith('subject:'):
            subject = subject[8:].strip()
        
        # Limit length
        if len(subject) > 80:
            subject = subject[:77] + "..."
        
        return subject
    
    def _is_valid_subject(self, subject: str) -> bool:
        """Validate generated subject line"""
        if not subject or len(subject.strip()) < 5:
            return False
        
        # Check for obviously bad outputs
        bad_indicators = [
            'i cannot', 'i can\'t', 'as an ai', 'sorry',
            'inappropriate', 'unable to', '```', 'here is',
            'here\'s a', 'here are'
        ]
        
        subject_lower = subject.lower()
        return not any(bad in subject_lower for bad in bad_indicators)
    
    def _default_subject(self, sender_name: str, company_name: Optional[str]) -> str:
        """Generate fallback subject line"""
        if company_name and company_name != "your organization":
            return f"Application for Position at {company_name} - {sender_name}"
        else:
            return f"Software Engineer Application - {sender_name}"
    
    def test_connection(self) -> dict:
        """Test Ollama connection and return status"""
        status = {
            "ollama_running": False,
            "model_available": False,
            "available_models": [],
            "message": ""
        }
        
        # Test if Ollama is running
        status["ollama_running"] = self.is_ollama_running()
        
        if not status["ollama_running"]:
            status["message"] = "Ollama service is not running. Start with 'ollama serve'"
            return status
        
        # Get available models
        status["available_models"] = self.get_available_models()
        
        # Test if our model is available
        status["model_available"] = self.is_model_available()
        
        if status["model_available"]:
            status["message"] = f"✅ {self.model} model ready"
        else:
            if status["available_models"]:
                status["message"] = f"⚠️  {self.model} not found. Available: {', '.join(status['available_models'][:3])}"
            else:
                status["message"] = f"⚠️  No models installed. Install with: ollama pull {self.model}"
        
        return status