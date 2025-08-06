# ChatBot Configuration Settings
# Modify these values to customize your chatbot behavior

class ChatBotConfig:
    """Configuration settings for the AI ChatBot"""
    
    # ===========================================
    # MEMORY SETTINGS
    # ===========================================
    
    # How many conversation pairs to remember
    # Lower values = less memory usage, faster responses
    # Higher values = more context, better conversations
    MEMORY_WINDOW = 20  # Default: 10, Recommended: 10-50
    
    # ===========================================
    # AI BEHAVIOR SETTINGS  
    # ===========================================
    
    # AI creativity level (0.0 = boring, 2.0 = very creative)
    TEMPERATURE = 0.7  # Default: 0.7, Recommended: 0.3-1.0
    
    # OpenAI model to use
    MODEL_NAME = "gpt-3.5-turbo"  # Options: gpt-3.5-turbo, gpt-4
    
    # ===========================================
    # KNOWLEDGE BASE SETTINGS
    # ===========================================
    
    # How many relevant documents to retrieve for knowledge queries
    KNOWLEDGE_RETRIEVAL_COUNT = 3  # Default: 3, Range: 1-10
    
    # Text chunk size for document processing
    CHUNK_SIZE = 1000  # Default: 1000, Range: 500-2000
    
    # Overlap between chunks (helps maintain context)
    CHUNK_OVERLAP = 200  # Default: 200, Range: 50-500
    
    # ===========================================
    # PERFORMANCE SETTINGS
    # ===========================================
    
    # Maximum file size for uploads (in MB)
    MAX_FILE_SIZE_MB = 10
    
    # Supported file types
    SUPPORTED_FILE_TYPES = [".txt", ".csv"]
    
    # ===========================================
    # MEMORY WINDOW PRESETS
    # ===========================================
    
    # Quick presets for different use cases
    MEMORY_PRESETS = {
        "minimal": 5,      # For simple Q&A, low memory usage
        "standard": 10,    # Default balanced setting
        "extended": 20,    # For longer conversations
        "comprehensive": 50,  # For complex multi-topic discussions
        "maximum": 100     # For very long context (high memory usage)
    }
    
    @classmethod
    def get_memory_preset(cls, preset_name: str) -> int:
        """Get memory window size for a preset"""
        return cls.MEMORY_PRESETS.get(preset_name, cls.MEMORY_WINDOW)
    
    @classmethod
    def get_memory_usage_estimate(cls, memory_window: int) -> str:
        """Estimate memory usage for a given window size"""
        if memory_window <= 10:
            return "Low memory usage"
        elif memory_window <= 30:
            return "Medium memory usage"
        elif memory_window <= 60:
            return "High memory usage"
        else:
            return "Very high memory usage" 