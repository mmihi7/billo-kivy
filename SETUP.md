# Billo POS - Setup Instructions

## Prerequisites

1. Python 3.8 or higher
2. pip (Python package manager)
3. Supabase account (https://supabase.com/)

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd billo-kivy
   ```

2. **Create and activate a virtual environment**
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate
   
   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   - Copy `.env.example` to `.env`
   - Fill in your Supabase credentials:
     ```
     SUPABASE_URL=your_supabase_project_url
     SUPABASE_KEY=your_supabase_anon_key
     ```

## Database Setup

1. **Set up Supabase**
   - Create a new project in Supabase
   - Go to the SQL editor and run the schema from `supabase/schema.sql`
   - Enable Row Level Security (RLS) and set up appropriate policies

2. **Initialize local database**
   ```bash
   python -c "from shared.database import db; db.create_tables()"
   ```

## Running the Application

### Customer App (Mobile)
```bash
python customer_app/main.py
```

### Restaurant App (Desktop)
```bash
python restaurant_app/main.py
```

## Development

### Code Style
- Follow PEP 8 guidelines
- Use type hints where possible
- Document functions and classes with docstrings

### Testing
```bash
pytest
```

### Linting
```bash
flake8
```

### Formatting
```bash
black .
```

## Deployment

### Android (Customer App)
1. Install Buildozer:
   ```bash
   pip install buildozer
   pip install cython==0.29.33
   ```

2. Configure buildozer.spec

3. Build APK:
   ```bash
   buildozer -v android debug
   ```

### Desktop (Restaurant App)
Package using PyInstaller or similar tool for the target platform.

## Troubleshooting

- If you encounter any issues, check the logs in the `logs/` directory
- Make sure all environment variables are set correctly
- Ensure all dependencies are installed
