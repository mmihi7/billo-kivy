# Billo POS System

A modern, tab-based Point of Sale system for restaurants and bars, built with Python, Kivy/KivyMD, and Supabase.

## Project Structure

- `customer_app/` - Mobile app for customers (Android/iOS)
- `restaurant_app/` - Desktop app for restaurant staff (Windows/macOS/Linux)
- `shared/` - Shared code and utilities
- `supabase/` - Database migrations and configurations
- `docs/` - Project documentation
- `tests/` - Test files

## Getting Started

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- Supabase account
- Android Studio (for Android builds)
- Xcode (for iOS builds, macOS only)

### Installation
1. Clone the repository
2. Create and activate a virtual environment
3. Install dependencies: `pip install -r requirements.txt`

## Development

### Customer App
```bash
cd customer_app
python main.py
```

### Restaurant App
```bash
cd restaurant_app
python main.py
```

## License
MIT
