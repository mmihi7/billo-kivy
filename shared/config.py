import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

class Config:
    # Supabase Configuration
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY')
    
    # App Configuration
    APP_NAME = "Billo POS"
    VERSION = "0.1.0"
    
    # Database
    DB_NAME = "billo.db"
    
    # Realtime
    REALTIME_ENABLED = True

    @classmethod
    def validate(cls):
        """Validate that all required environment variables are set."""
        required_vars = ['SUPABASE_URL', 'SUPABASE_KEY']
        missing = [var for var in required_vars if not getattr(cls, var, None)]
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

# Validate configuration on import
Config.validate()
