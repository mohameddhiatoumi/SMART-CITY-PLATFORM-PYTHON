# 🔧 Setup Guide — Smart City Platform Neo-Sousse 2030

Complete step-by-step setup instructions.

## Prerequisites

- Python 3.10+
- PostgreSQL 14+
- Git

## 1. Python Environment

```bash
# Clone repository
git clone <repo-url>
cd smart-city-platform-python

# Create virtual environment
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## 2. PostgreSQL Setup

### Install PostgreSQL (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### Install PostgreSQL (macOS)
```bash
brew install postgresql@14
brew services start postgresql@14
```

### Create Database and User
```bash
sudo -u postgres psql
```

In the PostgreSQL shell:
```sql
CREATE USER smartcity WITH PASSWORD 'your_password';
CREATE DATABASE smart_city_db OWNER smartcity;
GRANT ALL PRIVILEGES ON DATABASE smart_city_db TO smartcity;
\q
```

## 3. Environment Variables

```bash
cp .env.example .env
```

Edit `.env`:
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=smart_city_db
DB_USER=smartcity
DB_PASSWORD=your_password

OPENAI_API_KEY=sk-...  # Optional for AI reports

DEBUG=True
LOG_LEVEL=INFO
SECRET_KEY=change-this-in-production
```

## 4. Database Initialization

```bash
# Create all tables, views, and indexes
python main.py init-db

# Seed with 1000+ realistic records
python main.py seed-data
```

## 5. Verify Setup

```bash
# Run demo (no DB required)
python main.py demo

# Test compiler
python main.py compile-query "Show the 5 most polluted zones"

# Run tests
pytest tests/ -v
```

## 6. Launch Dashboard

```bash
streamlit run dashboard/app.py
```

Open your browser at: http://localhost:8501

## 7. Using the CLI

```bash
# Initialize database
python main.py init-db

# Seed data
python main.py seed-data

# Compile a query
python main.py compile-query "List all active sensors"

# Run interactive demo
python main.py demo

# Launch dashboard
python main.py dashboard
```

## Troubleshooting

### Database Connection Issues
```
ERROR: could not connect to server
```
- Check PostgreSQL is running: `sudo systemctl status postgresql`
- Verify `.env` credentials
- Test connection: `psql -h localhost -U smartcity -d smart_city_db`

### Module Not Found Errors
```
ModuleNotFoundError: No module named 'xxx'
```
- Ensure venv is activated: `source venv/bin/activate`
- Reinstall: `pip install -r requirements.txt`
- Run from project root directory

### OpenAI API Key
- AI reports work without an API key (template mode)
- Set `OPENAI_API_KEY` in `.env` to enable GPT-powered reports
- Reports gracefully fallback to templates if key is missing

### Streamlit Port Already in Use
```bash
streamlit run dashboard/app.py --server.port 8502
```

### Running Tests Without Database
All tests are designed to work without a live database:
```bash
pytest tests/ -v
```

## Development Notes

- The compiler uses pure Python regex — no NLTK/spaCy required
- DFA engines work fully in-memory
- Dashboard uses demo data when DB is unavailable
- AI reports use template fallback without OpenAI API key
