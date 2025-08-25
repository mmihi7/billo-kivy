from datetime import datetime, timedelta
import random
import uuid

# Sample restaurant data
RESTAURANT_DATA = {
    "id": "demo_restaurant_123",
    "name": "Nairobi Bistro",
    "address": "123 Test Street, Nairobi",
    "phone": "+254700123456",
    "email": "info@nairobbistro.com",
    "is_active": True,
    "created_at": datetime.utcnow().isoformat(),
    "menu_items": [
        {"id": "item_1", "name": "Calamari", "price": 1200, "category": "Starters"},
        {"id": "item_2", "name": "Bruschetta", "price": 800, "category": "Starters"},
        {"id": "item_3", "name": "Grilled Salmon", "price": 2200, "category": "Mains"},
        {"id": "item_4", "name": "Beef Burger", "price": 1500, "category": "Mains"},
        {"id": "item_5", "name": "Coke", "price": 200, "category": "Drinks"},
        {"id": "item_6", "name": "Water", "price": 100, "category": "Drinks"},
    ]
}

# Sample staff members who can serve customers
SERVERS = [
    {"id": "srv_1", "name": "Alex DC", "initials": "ADC"},
    {"id": "srv_2", "name": "Grace DR", "initials": "GDR"},
]

# Generate sample customer tabs
def generate_sample_tabs(count=3):
    tabs = []
    
    # Sample customer names
    customers = [
        "John Mwangi",
        "Sarah Ochieng",
        "David Kimani",
        "Grace Atieno",
        "Michael Omondi"
    ]
    
    for i in range(1, count + 1):
        tab_id = f"tab_{i:03d}"  # Format as 001, 002, etc.
        customer = customers[i % len(customers)]
        server = random.choice(SERVERS)
        
        # Generate orders for this tab
        orders = generate_sample_orders()
        total = sum(order["total_price"] for order in orders)
        
        tab = {
            "id": tab_id,
            "number": i,
            "customer_name": customer,
            "status": "open",
            "total": total,
            "server_id": server["id"],
            "server_name": server["name"],
            "server_initials": server["initials"],
            "created_at": (datetime.utcnow() - timedelta(hours=random.randint(1, 24))).isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "orders": orders
        }
        tabs.append(tab)
    
    return tabs

def generate_sample_orders():
    orders = []
    menu_items = RESTAURANT_DATA["menu_items"]
    
    # Create 1-4 orders per tab
    for _ in range(random.randint(1, 4)):
        item = random.choice(menu_items)
        quantity = random.randint(1, 3)
        server = random.choice(SERVERS)
        
        order = {
            "id": f"ord_{uuid.uuid4().hex[:8]}",
            "menu_item_id": item["id"],
            "name": item["name"],
            "quantity": quantity,
            "unit_price": item["price"],
            "total_price": item["price"] * quantity,
            "category": item["category"],
            "notes": "No onions" if random.random() > 0.7 else "",
            "server_id": server["id"],
            "server_initials": server["initials"],
            "timestamp": datetime.utcnow().isoformat()
        }
        orders.append(order)
    
    return orders

def get_test_data():
    """Return all test data in a single dictionary."""
    return {
        "restaurant": RESTAURANT_DATA,
        "servers": SERVERS,
        "tabs": generate_sample_tabs(3),  # Generate 3 sample customer tabs
        "current_server": SERVERS[0]  # Set first server as current
    }

if __name__ == "__main__":
    # Print sample data when run directly
    import json
    print(json.dumps(get_test_data(), indent=2, default=str))
