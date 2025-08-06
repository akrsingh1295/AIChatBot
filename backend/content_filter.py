"""
Content Filtering and Moderation System for AI ChatBot
Prevents inappropriate content, sexual content, and controversial documents
"""

import re
import hashlib
import mimetypes
from typing import List, Dict, Tuple, Optional
from pathlib import Path
import logging
from openai import OpenAI
import json

# Setup logging
logger = logging.getLogger(__name__)

class ContentFilter:
    """Advanced content filtering and moderation system"""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """Initialize content filter with various filtering methods"""
        self.openai_client = OpenAI(api_key=openai_api_key) if openai_api_key else None
        
        # Blocked words and phrases (comprehensive list)
        self.blocked_words = {
            # Sexual content
            'sexual', 'nsfw', 'porn', 'sex', 'nude', 'naked', 'adult', 'xxx',
            'erotic', 'fetish', 'kinky', 'orgasm', 'masturbat', 'sexual',
            
            # Hate speech and discrimination  
            'racist', 'nazi', 'terrorism', 'terrorist', 'bomb', 'kill',
            'murder', 'suicide', 'violence', 'hate', 'discriminat',
            
            # Controversial political content
            'revolution', 'overthrow', 'coup', 'extremist', 'radical',
            
            # Inappropriate requests
            'hack', 'crack', 'piracy', 'illegal', 'drug', 'weapon'
        }
        
        # Blocked file types
        self.blocked_extensions = {
            '.exe', '.bat', '.cmd', '.com', '.scr', '.pif', '.vbs', '.js',
            '.jar', '.app', '.deb', '.rpm', '.dmg', '.pkg', '.msi'
        }
        
        # Allowed document types only
        self.allowed_extensions = {
            '.txt', '.csv', '.pdf', '.docx', '.doc', '.md', '.json'
        }
        
        # Maximum file size (10MB)
        self.max_file_size = 10 * 1024 * 1024
        
        # Suspicious patterns
        self.suspicious_patterns = [
            r'\b(?:how\s+to\s+(?:make|build|create))\s+(?:bomb|weapon|drug)\b',
            r'\b(?:suicide|kill\s+myself)\b',
            r'\b(?:hack|crack|break\s+into)\b',
            r'\b(?:download|stream|watch)\s+(?:porn|adult|xxx)\b',
            r'\b(?:nude|naked)\s+(?:photos|images|pics)\b'
        ]
    
    def check_text_content(self, text: str) -> Tuple[bool, str]:
        """
        Check if text content is appropriate
        Returns: (is_safe, reason_if_blocked)
        """
        if not text:
            return True, ""
        
        text_lower = text.lower()
        
        # 1. Check for blocked words
        for word in self.blocked_words:
            if word in text_lower:
                logger.warning(f"Blocked content detected: {word}")
                return False, f"Content contains inappropriate material: '{word}'"
        
        # 2. Check for suspicious patterns
        for pattern in self.suspicious_patterns:
            if re.search(pattern, text_lower):
                logger.warning(f"Suspicious pattern detected: {pattern}")
                return False, "Content contains potentially harmful requests"
        
        # 3. Check content length
        if len(text) > 10000:  # 10k character limit
            return False, "Message too long. Please keep messages under 10,000 characters"
        
        # 4. Use OpenAI Moderation API if available
        if self.openai_client:
            try:
                moderation = self.openai_client.moderations.create(input=text)
                if moderation.results[0].flagged:
                    categories = [cat for cat, flagged in moderation.results[0].categories.__dict__.items() if flagged]
                    return False, f"Content flagged for: {', '.join(categories)}"
            except Exception as e:
                logger.warning(f"OpenAI moderation check failed: {e}")
        
        return True, ""
    
    def check_file_upload(self, file_path: str, file_content: bytes) -> Tuple[bool, str]:
        """
        Check if uploaded file is safe and appropriate
        Returns: (is_safe, reason_if_blocked)
        """
        # 1. Check file size
        if len(file_content) > self.max_file_size:
            return False, f"File too large. Maximum size is {self.max_file_size // (1024*1024)}MB"
        
        # 2. Check file extension
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext in self.blocked_extensions:
            return False, f"File type '{file_ext}' is not allowed for security reasons"
        
        if file_ext not in self.allowed_extensions:
            return False, f"Only these file types are allowed: {', '.join(self.allowed_extensions)}"
        
        # 3. Check file content for text files
        if file_ext in ['.txt', '.csv', '.md', '.json']:
            try:
                text_content = file_content.decode('utf-8', errors='ignore')
                is_safe, reason = self.check_text_content(text_content)
                if not is_safe:
                    return False, f"File contains inappropriate content: {reason}"
            except Exception as e:
                logger.warning(f"Could not analyze file content: {e}")
        
        # 4. Check for malicious file signatures
        if self._is_potentially_malicious(file_content):
            return False, "File appears to contain executable or potentially harmful content"
        
        return True, ""
    
    def _is_potentially_malicious(self, file_content: bytes) -> bool:
        """Check for potentially malicious file signatures"""
        # Check for executable signatures
        malicious_signatures = [
            b'MZ',  # DOS/Windows executable
            b'\x7fELF',  # Linux executable
            b'\xca\xfe\xba\xbe',  # Java class file
            b'PK\x03\x04',  # ZIP file (could contain executables)
        ]
        
        for signature in malicious_signatures:
            if file_content.startswith(signature):
                return True
        
        return False
    
    def sanitize_filename(self, filename: str) -> str:
        """Sanitize filename to prevent directory traversal attacks"""
        # Remove any path components
        filename = Path(filename).name
        
        # Remove dangerous characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        
        # Limit filename length
        if len(filename) > 255:
            name, ext = Path(filename).stem, Path(filename).suffix
            filename = name[:255-len(ext)] + ext
        
        return filename
    
    def check_knowledge_base_content(self, content: str) -> Tuple[bool, str]:
        """
        Special check for knowledge base content
        More strict filtering for company knowledge bases
        """
        # All regular text checks
        is_safe, reason = self.check_text_content(content)
        if not is_safe:
            return is_safe, reason
        
        # Additional checks for business content
        business_red_flags = [
            'confidential', 'secret', 'password', 'api_key', 'private_key',
            'social_security', 'ssn', 'credit_card', 'bank_account'
        ]
        
        content_lower = content.lower()
        for flag in business_red_flags:
            if flag in content_lower:
                return False, f"Document contains sensitive information: {flag}"
        
        return True, ""
    
    def generate_content_hash(self, content: str) -> str:
        """Generate hash for content deduplication and tracking"""
        return hashlib.sha256(content.encode()).hexdigest()
    
    def get_content_category(self, text: str) -> str:
        """Categorize content type for logging and analytics"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['question', 'help', 'how', 'what', 'why']):
            return 'question'
        elif any(word in text_lower for word in ['thank', 'thanks', 'good', 'great']):
            return 'appreciation'
        elif any(word in text_lower for word in ['problem', 'issue', 'error', 'wrong']):
            return 'problem_report'
        else:
            return 'general'

class ContentModerationLogger:
    """Log content moderation events for security monitoring"""
    
    def __init__(self):
        self.logger = logging.getLogger('content_moderation')
        
    def log_blocked_content(self, content_type: str, reason: str, user_ip: str = None):
        """Log when content is blocked"""
        self.logger.warning(f"BLOCKED: {content_type} - {reason} - IP: {user_ip}")
    
    def log_file_upload(self, filename: str, file_size: int, status: str, user_ip: str = None):
        """Log file upload attempts"""
        self.logger.info(f"FILE_UPLOAD: {filename} ({file_size} bytes) - {status} - IP: {user_ip}")
    
    def log_suspicious_activity(self, activity: str, details: str, user_ip: str = None):
        """Log suspicious user activity"""
        self.logger.warning(f"SUSPICIOUS: {activity} - {details} - IP: {user_ip}")

# Pre-configured content filters for different use cases
class BusinessContentFilter(ContentFilter):
    """Stricter content filter for business environments"""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        super().__init__(openai_api_key)
        
        # Additional business-specific blocked words
        self.blocked_words.update({
            'competitor', 'lawsuit', 'legal_action', 'whistleblow',
            'insider_trading', 'embezzle', 'fraud', 'bribe'
        })

class EducationalContentFilter(ContentFilter):
    """Content filter optimized for educational environments"""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        super().__init__(openai_api_key)
        
        # More lenient for educational discussions but still safe
        educational_exceptions = {
            'biology', 'anatomy', 'reproduction', 'health', 'medical'
        }
        
        # Remove some words that might be needed for education
        self.blocked_words = {word for word in self.blocked_words 
                             if word not in educational_exceptions}

# Usage example and testing
def test_content_filter():
    """Test the content filtering system"""
    filter_system = ContentFilter()
    
    test_cases = [
        "Hello, how can I help you today?",  # Safe
        "Can you help me with Python programming?",  # Safe
        "How to make a bomb",  # Should be blocked
        "I want to see nude photos",  # Should be blocked
        "What is machine learning?",  # Safe
    ]
    
    print("Content Filter Test Results:")
    print("-" * 40)
    
    for text in test_cases:
        is_safe, reason = filter_system.check_text_content(text)
        status = "✅ SAFE" if is_safe else "❌ BLOCKED"
        print(f"{status}: '{text[:50]}...'")
        if not is_safe:
            print(f"    Reason: {reason}")

if __name__ == "__main__":
    test_content_filter() 