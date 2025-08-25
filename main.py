#!/usr/bin/env python3
"""
Billo POS System - Main Entry Point
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add the project root to the Python path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    from customer_app.app import BilloCustomerApp
    BilloCustomerApp().run()
