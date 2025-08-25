"""
Test script to verify database setup and basic operations.
"""
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

def test_database_connection():
    """Test database connection and table creation."""
    from shared.database import db
    from shared.models.base import Base
    from shared.models.core import User, Restaurant, Tab, Order, MenuItem, Waiter, Payment, Message
    
    print("Testing database connection...")
    
    try:
        # Create tables
        db.create_tables()
        print("✅ Database tables created successfully")
        
        # Test inserting a restaurant
        from sqlalchemy.orm import sessionmaker
        from sqlalchemy import create_engine
        
        Session = sessionmaker(bind=db.engine)
        session = Session()
        
        # Create a test restaurant
        restaurant = Restaurant(
            id="test_restaurant_1",
            name="Test Restaurant",
            county="Nairobi",
            location="Westlands",
            business_hours={"monday": "09:00-22:00", "tuesday": "09:00-22:00"}
        )
        
        session.add(restaurant)
        session.commit()
        print("✅ Test restaurant created successfully")
        
        # Query the restaurant
        test_restaurant = session.query(Restaurant).filter_by(name="Test Restaurant").first()
        if test_restaurant:
            print(f"✅ Found restaurant: {test_restaurant.name} in {test_restaurant.location}")
        else:
            print("❌ Failed to find test restaurant")
        
        # Clean up
        session.delete(test_restaurant)
        session.commit()
        session.close()
        
        print("✅ Database test completed successfully")
        
    except Exception as e:
        print(f"❌ Database test failed: {str(e)}")
        raise

if __name__ == "__main__":
    test_database_connection()
