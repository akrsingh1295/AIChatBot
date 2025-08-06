"""
Content Filter Configuration
Customize content filtering rules for your specific use case
"""

class ContentFilterConfig:
    """Configuration for content filtering system"""
    
    # ===========================================
    # CONTENT FILTERING SETTINGS
    # ===========================================
    
    # Filter strictness level
    FILTER_LEVEL = "strict"  # Options: "strict", "moderate", "lenient"
    
    # Use OpenAI Moderation API
    USE_OPENAI_MODERATION = True  # Recommended for best filtering
    
    # Maximum message length (characters)
    MAX_MESSAGE_LENGTH = 10000
    
    # Maximum number of files per upload
    MAX_FILES_PER_UPLOAD = 10
    
    # Maximum total file size (MB)
    MAX_TOTAL_FILE_SIZE_MB = 50
    
    # Maximum individual file size (MB)
    MAX_INDIVIDUAL_FILE_SIZE_MB = 10
    
    # ===========================================
    # ALLOWED FILE TYPES
    # ===========================================
    
    ALLOWED_FILE_EXTENSIONS = {
        '.txt',   # Plain text
        '.csv',   # Comma-separated values
        '.md',    # Markdown
        '.json',  # JSON data
        '.pdf',   # PDF documents (if you add PDF support)
        '.docx',  # Word documents (if you add Word support)
    }
    
    # ===========================================
    # BLOCKED CONTENT CATEGORIES
    # ===========================================
    
    # Sexual content
    BLOCK_SEXUAL_CONTENT = True
    
    # Violence and hate speech
    BLOCK_VIOLENCE = True
    
    # Illegal activities
    BLOCK_ILLEGAL_CONTENT = True
    
    # Self-harm content
    BLOCK_SELF_HARM = True
    
    # Controversial political content
    BLOCK_POLITICAL_EXTREMISM = True
    
    # ===========================================
    # CUSTOM BLOCKED WORDS
    # ===========================================
    
    # Add your own custom blocked words/phrases
    CUSTOM_BLOCKED_WORDS = {
        # Add industry-specific terms if needed
        # Example: 'confidential_project_name', 'internal_code_word'
    }
    
    # ===========================================
    # BUSINESS-SPECIFIC SETTINGS
    # ===========================================
    
    # Block competitor mentions (add your competitors)
    BLOCK_COMPETITORS = {
        # Example: 'competitor_name', 'rival_company'
    }
    
    # Block sensitive business topics
    BLOCK_SENSITIVE_BUSINESS = {
        'layoffs', 'downsizing', 'bankruptcy', 'acquisition',
        'merger', 'confidential', 'internal_only'
    }
    
    # ===========================================
    # WHITELIST (ALLOWED EXCEPTIONS)
    # ===========================================
    
    # Educational or medical terms that might otherwise be blocked
    EDUCATIONAL_WHITELIST = {
        'biology', 'anatomy', 'medical', 'health', 'science',
        'reproduction', 'genetics', 'physiology'
    }
    
    # ===========================================
    # LOGGING AND MONITORING
    # ===========================================
    
    # Log all blocked content attempts
    LOG_BLOCKED_CONTENT = True
    
    # Log all file uploads
    LOG_FILE_UPLOADS = True
    
    # Alert on suspicious patterns (multiple blocks from same IP)
    ALERT_ON_SUSPICIOUS_ACTIVITY = True
    
    # Number of blocked attempts before flagging IP as suspicious
    SUSPICIOUS_ACTIVITY_THRESHOLD = 5
    
    # ===========================================
    # RESPONSE MESSAGES
    # ===========================================
    
    # Message shown when content is blocked
    BLOCKED_CONTENT_MESSAGE = "I cannot provide information on that topic. Please ask something else."
    
    # Message shown when file is rejected
    BLOCKED_FILE_MESSAGE = "This file cannot be uploaded due to content policy restrictions."
    
    # ===========================================
    # FILTER PRESETS
    # ===========================================
    
    FILTER_PRESETS = {
        "strict": {
            "use_openai_moderation": True,
            "block_all_categories": True,
            "custom_word_sensitivity": "high"
        },
        "moderate": {
            "use_openai_moderation": True,
            "block_all_categories": True,
            "custom_word_sensitivity": "medium",
            "educational_exceptions": True
        },
        "lenient": {
            "use_openai_moderation": True,
            "block_only_explicit": True,
            "custom_word_sensitivity": "low",
            "educational_exceptions": True
        }
    }
    
    @classmethod
    def get_active_config(cls):
        """Get the active configuration based on filter level"""
        return cls.FILTER_PRESETS.get(cls.FILTER_LEVEL, cls.FILTER_PRESETS["strict"])
    
    @classmethod
    def is_educational_context(cls, text: str) -> bool:
        """Check if text appears to be in educational context"""
        educational_indicators = [
            'learn', 'teach', 'study', 'education', 'course', 'lesson',
            'academic', 'research', 'science', 'university', 'school'
        ]
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in educational_indicators)

# Environment-specific configurations
class DevelopmentConfig(ContentFilterConfig):
    """Less strict filtering for development/testing"""
    FILTER_LEVEL = "lenient"
    LOG_BLOCKED_CONTENT = True
    ALERT_ON_SUSPICIOUS_ACTIVITY = False

class ProductionConfig(ContentFilterConfig):
    """Strict filtering for production environment"""
    FILTER_LEVEL = "strict"
    USE_OPENAI_MODERATION = True
    LOG_BLOCKED_CONTENT = True
    ALERT_ON_SUSPICIOUS_ACTIVITY = True

class EducationConfig(ContentFilterConfig):
    """Balanced filtering for educational institutions"""
    FILTER_LEVEL = "moderate"
    USE_OPENAI_MODERATION = True
    
    # More lenient with educational content
    CUSTOM_BLOCKED_WORDS = ContentFilterConfig.CUSTOM_BLOCKED_WORDS - {
        'sex', 'sexual'  # Allow in educational context
    }

class BusinessConfig(ContentFilterConfig):
    """Enterprise-focused filtering"""
    FILTER_LEVEL = "strict"
    
    # Additional business-specific blocks
    CUSTOM_BLOCKED_WORDS = ContentFilterConfig.CUSTOM_BLOCKED_WORDS.union({
        'confidential', 'proprietary', 'trade_secret', 'internal_only'
    })

# Helper function to get appropriate config
def get_content_filter_config(environment: str = "production"):
    """Get content filter configuration based on environment"""
    configs = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
        "education": EducationConfig,
        "business": BusinessConfig
    }
    return configs.get(environment, ProductionConfig) 