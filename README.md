# 🏙️ Smart City Analytics Platform — Neo-Sousse 2030

A comprehensive smart city analytics platform for Neo-Sousse 2030, featuring:
- **Natural Language to SQL Compiler** — Write queries in plain English
- **DFA State Machines** — Monitor sensors, interventions, and vehicles
- **AI-Generated Reports** — Intelligent city health analysis
- **Interactive Dashboard** — Real-time Streamlit web app
- **PostgreSQL Database** — Full relational data model with 1000+ seed records

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│              Smart City Platform — Neo-Sousse 2030              │
├─────────────────────────────────────────────────────────────────┤
│  Dashboard (Streamlit)  │  Compiler (NL→SQL)  │  Automata DFA  │
│  ├─ Home/Analytics      │  ├─ Lexer            │  ├─ Sensor DFA │
│  ├─ Query Builder       │  ├─ Parser           │  ├─ Intervention│
│  ├─ AI Reports          │  ├─ Code Generator   │  ├─ Vehicle DFA │
│  └─ Automata Viewer     │  └─ Query Builder    │  └─ Alerts     │
├─────────────────────────────────────────────────────────────────┤
│              AI Module (LangChain + Template Fallback)          │
├─────────────────────────────────────────────────────────────────┤
│              PostgreSQL Database (SQLAlchemy ORM)               │
│  Tables: Arrondissement, Zone, Capteur, Citoyen, Vehicule,     │
│          Trajet, Technicien, Intervention, Affecte,            │
│          Mesure_Capteur, System_IA, Consultation                │
└─────────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone <repo-url>
cd smart-city-platform-python
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your database credentials
```

### 3. Initialize Database

```bash
python main.py init-db
python main.py seed-data
```

### 4. Launch Dashboard

```bash
streamlit run dashboard/app.py
```

### 5. Run CLI Demo

```bash
python main.py demo
```

## 📦 Module Overview

### Compiler (NL→SQL)

Convert natural language to SQL without any external NLP dependencies:

```python
from compiler.query_builder import QueryBuilder

builder = QueryBuilder()
result = builder.build("Show the 5 most polluted zones")
print(result['sql'])
# SELECT * FROM Zone ORDER BY Indice_Pollution DESC LIMIT 5
```

**Supported query patterns:**
- `Show the N most [adjective] [entity]` → SELECT with ORDER BY + LIMIT
- `Which [entity] have [field] > [value]?` → SELECT with WHERE
- `List all [adjective] [entity]` → SELECT with WHERE
- `How many [entity] are [adjective]?` → SELECT COUNT
- `Count [entity] by [field]` → GROUP BY query
- `Average [field] of [entity]` → AVG aggregation

### Automata (DFA State Machines)

```python
from automata.sensor_dfa import SensorDFA
from automata.intervention_dfa import InterventionDFA
from automata.vehicle_dfa import VehicleDFA

# Sensor lifecycle
sensor = SensorDFA(sensor_id=1)
sensor.process_event("activate")      # INACTIVE → ACTIVE
sensor.process_event("signal_fault")  # ACTIVE → SIGNALED

# Intervention workflow
intervention = InterventionDFA(intervention_id=1)
intervention.process_event("assign_tech1")   # DEMAND → TECH1_ASSIGNED
intervention.process_event("validate_tech2") # → TECH2_VALIDATED
intervention.process_event("validate_ai")    # → AI_VALIDATED
intervention.process_event("complete")       # → COMPLETED

# Vehicle trajectory
vehicle = VehicleDFA(vehicle_id=1)
vehicle.process_event("depart")    # PARKED → EN_ROUTE
vehicle.process_event("arrive")    # EN_ROUTE → ARRIVED
vehicle.process_event("return")    # ARRIVED → PARKED
```

### AI Reports

```python
from ai.report_generator import ReportGenerator

gen = ReportGenerator(use_openai=False)  # Template mode (no API key needed)
report = gen.generate_city_dashboard_report({
    "active_sensors": 42,
    "interventions_pending": 7,
    "avg_pollution": 35.2,
    "citizens": 30,
})
```

### Database Models

```python
from models import Capteur, Zone, Intervention, Citoyen
from models.base import get_session

session = get_session()
active_sensors = session.query(Capteur).filter_by(Statut="ACTIVE").all()
polluted_zones = session.query(Zone).order_by(Zone.Indice_Pollution.desc()).limit(5).all()
```

## 🔍 Example Queries

| Natural Language | Generated SQL |
|-----------------|---------------|
| Show the 5 most polluted zones | `SELECT * FROM Zone ORDER BY Indice_Pollution DESC LIMIT 5` |
| Which citizens have an ecological score > 80 | `SELECT * FROM Citoyen WHERE Score_Ecologique > 80` |
| List all active sensors | `SELECT * FROM Capteur WHERE Statut = 'ACTIVE'` |
| How many interventions are AI validated | `SELECT COUNT(*) AS total FROM Intervention WHERE Valide_IA = TRUE` |
| Count sensors by type | `SELECT Type_Capteur, COUNT(*) AS total FROM Capteur GROUP BY Type_Capteur ORDER BY total DESC` |
| Average ecological score of citizens | `SELECT AVG(Score_Ecologique) AS result FROM Citoyen` |

## 🧪 Running Tests

```bash
# All tests (no database required)
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=. --cov-report=html

# Specific module
pytest tests/test_compiler.py -v
pytest tests/test_automata.py -v
pytest tests/test_database.py -v
```

## 📁 Project Structure

```
smart-city-platform-python/
├── ai/                    # AI report generator
├── automata/              # DFA state machines
├── compiler/              # NL→SQL compiler
├── config/                # Settings & configuration
├── dashboard/             # Streamlit web app
│   ├── components/        # Reusable UI components
│   └── pages/             # Dashboard pages
├── database/              # Schema & seed data
├── models/                # SQLAlchemy ORM models
├── tests/                 # Test suite
├── main.py                # CLI entry point
├── requirements.txt       # Dependencies
└── .env.example           # Environment template
```

## 🌍 Data Coverage

The platform includes realistic data for **Sousse, Tunisia**:
- **5 Arrondissements**: Sousse Ville, Hammam Sousse, Akouda, Kalaa Kebira, Msaken
- **20 Zones** with realistic GPS coordinates
- **50 Sensors** across all zone types
- **1000+ sensor readings** with quality metrics
- **50 interventions** with full DFA state tracking
- **30 citizens** with Tunisian names and ecological scores
- **20 vehicles** with Tunisian plate numbers

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/my-feature`
3. Run tests: `pytest tests/ -v`
4. Commit: `git commit -m 'Add my feature'`
5. Push and open a Pull Request

## 📄 License

MIT License — Neo-Sousse 2030 Smart City Initiative
