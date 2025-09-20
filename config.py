"""
Configuration settings for the agentic workflow demo.
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for the agentic workflow."""
    
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
    
    # Agent Configuration
    MAX_ITERATIONS = int(os.getenv("MAX_ITERATIONS", "5"))
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
    MODEL_NAME = os.getenv("MODEL_NAME", "gpt-3.5-turbo")
    
    # GitHub API Configuration
    GITHUB_API_BASE = "https://api.github.com"
    
    # Validation
    @classmethod
    def validate(cls):
        """Validate required configuration."""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required. Please set it in your environment or .env file.")
        return True
