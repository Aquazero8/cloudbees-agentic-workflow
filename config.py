"""
Configuration settings for the agentic workflow demo.
"""
import os
from dotenv import load_dotenv

# Load environment variables
# Try to load .env file, with helpful error message if not found
if not load_dotenv():
    print("Warning: .env file not found. Make sure you have created a .env file with your API keys.")

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
            raise ValueError(
                "OPENAI_API_KEY is required. Please:\n"
                "1. Create a file named exactly '.env' (not 'touch.env' or any other name)\n"
                "2. Add: OPENAI_API_KEY=your_actual_api_key_here\n"
                "3. Make sure the .env file is in the same directory as the script"
            )
        return True
