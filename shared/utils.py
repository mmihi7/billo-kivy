import os
import json
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

class Utils:
    @staticmethod
    def get_project_root() -> Path:
        ""Get the project root directory."""
        return Path(__file__).parent.parent

    @staticmethod
    def create_directory(path: str) -> None:
        ""Create a directory if it doesn't exist."""
        os.makedirs(path, exist_ok=True)

    @staticmethod
    def load_json_file(file_path: str) -> Dict[str, Any]:
        ""Load JSON data from a file."""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    @staticmethod
    def save_json_file(file_path: str, data: Dict[str, Any]) -> None:
        ""Save data to a JSON file."""
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)

    @staticmethod
    def generate_id(prefix: str = '') -> str:
        ""Generate a unique ID with an optional prefix."""
        timestamp = int(datetime.utcnow().timestamp() * 1000)
        random_str = os.urandom(8).hex()
        return f"{prefix}{timestamp}_{random_str}"

    @staticmethod
    def hash_password(password: str, salt: Optional[str] = None) -> str:
        ""Hash a password with a salt."""
        if salt is None:
            salt = os.urandom(16).hex()
        
        hashed = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        )
        return f"{salt}${hashed.hex()}"

    @staticmethod
    def verify_password(stored_password: str, provided_password: str) -> bool:
        ""Verify a password against a stored hash."""
        try:
            salt, _ = stored_password.split('$')
            return stored_password == Utils.hash_password(provided_password, salt)
        except (ValueError, AttributeError):
            return False

    @staticmethod
    def format_currency(amount: float) -> str:
        ""Format a number as currency (KES)."""
        return f"KES {amount:,.2f}"

    @staticmethod
    def format_datetime(dt: datetime) -> str:
        ""Format a datetime object as a readable string."""
        return dt.strftime("%Y-%m-%d %H:%M:%S")
