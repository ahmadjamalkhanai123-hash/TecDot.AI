# TecDot.AI - Unified AI Engineering Platform

A unified, web-first AI Engineering Platform that lets users visually build, train, evaluate, deploy, and operate data and AI systems.

## Project Status

- **Current Milestone:** M1 - Platform Foundation
- **Technology Stack:** PostgreSQL + FastAPI + React + Docker
- **Status:** Initial setup in progress

## Architecture

This platform follows the approved master plan from the MCP project documentation:

- **Database:** PostgreSQL 15+ (confirmed)
- **Backend API:** FastAPI 0.110+
- **Frontend:** React 18 + TypeScript
- **Authentication:** JWT + PostgreSQL users
- **Workflow Engine:** Custom async Python
- **Containers:** Docker + Docker Compose
- **ML Frameworks:** PyTorch + scikit-learn

## M1 Goals - Platform Foundation

Create a real, verifiable visual workflow execution platform:

- [x] Project workspace structure
- [ ] Typed component contracts
- [ ] Visual graph editor (React Flow)
- [ ] Graph validation
- [ ] Execution service and isolated workers
- [ ] Run history, artifacts, logs, and versions

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- PGAdmin 4 (for database management)
- Node.js 18+ (for frontend)
- Docker & Docker Compose

### Setup PostgreSQL Database

1. Open PGAdmin
2. Create database: `unified_ai_platform_dev`
3. Update `.env` with your PostgreSQL credentials

### Backend Setup

```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload
```

Backend will run on: http://localhost:8000
API docs available at: http://localhost:8000/docs

### View in PGAdmin

1. Connect to `unified_ai_platform_dev` database
2. Navigate to: Schemas → public → Tables
3. See live data as the API creates records

## Project Structure

```
TecDot.AI/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── main.py      # FastAPI app
│   │   ├── config.py    # Settings
│   │   ├── database.py  # PostgreSQL connection
│   │   └── models/      # SQLAlchemy models
│   ├── alembic/         # Database migrations
│   └── pyproject.toml
├── frontend/            # React + TypeScript (coming soon)
├── docker-compose.yml   # PostgreSQL + Backend + Frontend
└── README.md
```

## Development Guidelines

Follow the project's approved principles:
- No fake or simulated functionality presented as real
- Security, observability, versioning designed from the start
- All changes must pass tests before commit
- See `QUALITY_GATES.md` in MCP docs for release requirements

## Documentation

Full project documentation available in the MCP starter package:
- Master Plan
- Architecture Decisions
- Technology Decision Records
- Quality Gates
- Milestone Specifications

## License

TBD
