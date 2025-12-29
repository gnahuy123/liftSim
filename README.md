# Lift Simulation Testbed

A lift simulation system for comparing elevator scheduling algorithms. Features a React frontend and FastAPI backend.

## Architecture

```
                    ┌─────────────────┐
                    │  React Frontend │  (port 5173 dev / served by FastAPI)
                    └────────┬────────┘
                             │ HTTP/WebSocket
                    ┌────────▼────────┐
                    │  FastAPI Backend │  (port 8000)
                    └────────┬────────┘
                             │
            ┌────────────────┼────────────────┐
            │                │                │
     ┌──────▼──────┐  ┌──────▼──────┐  ┌──────▼──────┐
     │ Building 1  │  │ Building 2  │  │  Sessions   │
     │ (2 Lifts)   │  │ (2 Lifts)   │  │  Manager    │
     └─────────────┘  └─────────────┘  └─────────────┘
```

## Prerequisites

- **Python** 3.10+
- **Node.js** 18+
- **npm** 9+

## Setup

### Backend

```bash
# Create virtual environment
python -m venv .venv

# Activate (Windows)
.\.venv\Scripts\activate

# Activate (Linux/macOS)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install dev dependencies (optional)
pip install -r requirements-dev.txt
```

### Frontend

```bash
cd frontend-react
npm install
```

## Running

### Development

```bash
# Terminal 1: Backend
uvicorn app.main:app --reload

# Terminal 2: Frontend
cd frontend-react
npm run dev
```

Open http://localhost:5173

### Production

```bash
# Build frontend
cd frontend-react
npm run build

# Start backend (serves built frontend)
uvicorn app.main:app
```

Open http://localhost:8000

### Docker

```bash
# Build and run with Docker Compose
docker compose up -d

# Or build manually
docker build -t lift-simulation .
docker run -p 8000:8000 lift-simulation
```

Open http://localhost:8000

## Testing

### Backend

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/ -v

# Run linter
ruff check app/

# Run type checker
mypy app/
```

### Frontend

```bash
cd frontend-react

# Run tests
npm test

# Run tests once
npm run test:run

# Format code
npm run format
```

## Pre-commit Hooks

```bash
# Install hooks
pip install pre-commit
pre-commit install

# Run manually
pre-commit run --all-files
```

## Project Structure

```
lift-backend/
├── app/
│   ├── api/           # FastAPI endpoints
│   ├── core/          # Business logic
│   │   ├── algorithms.py   # Lift algorithms
│   │   ├── building.py     # 2-lift building controller
│   │   ├── lift.py         # Single lift controller
│   │   └── multi_lift.py   # Multi-building comparison
│   └── models/        # Pydantic schemas
├── frontend-react/    # React + Vite frontend
├── tests/             # Python tests
└── requirements.txt   # Python dependencies
```

## Adding New Algorithms

Add to `app/core/algorithms.py`:

```python
class MyAlgorithm(LiftAlgorithm):
    name = "my_algo"
    description = "My custom algorithm"

    def pick_next_direction(self, current_level, current_direction, stops):
        # Your logic here
        return "up" | "down" | "idle"

# Register it
ALGORITHM_REGISTRY["my_algo"] = MyAlgorithm
```