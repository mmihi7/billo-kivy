"""
Test script to verify Supabase client setup and basic operations.
"""
import os
import sys
from dotenv import load_dotenv
from pathlib import Path

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

def test_supabase_connection():
    """Test Supabase connection and basic operations."""
    from shared.supabase_client import supabase
    
    print("Testing Supabase connection...")
    
    try:
        # Test connection by getting the auth settings
        settings = supabase.client.auth.get_settings()
        print("✅ Successfully connected to Supabase")
        print(f"Site URL: {settings.get('SITE_URL')}")
        
        # Test inserting a test record (if you have the tables set up)
        try:
            # This is just a test - adjust table and fields according to your schema
            test_data = {
                "name": "Test Item",
                "description": "This is a test item"
            }
            
            # Uncomment and modify this when you have your tables set up
            # result = supabase.client.table('test_table').insert(test_data).execute()
            # print("✅ Test data inserted successfully")
            # print(f"Inserted data: {result.data}")
            
        except Exception as e:
            print(f"⚠️ Test data insertion skipped or failed: {str(e)}")
            print("  Make sure you have set up your Supabase tables correctly.")
        
        print("✅ Supabase test completed successfully")
        
    except Exception as e:
        print(f"❌ Supabase test failed: {str(e)}")
        print("  Please check your Supabase URL and API key in the .env file")
        raise

if __name__ == "__main__":
    test_supabase_connection()
