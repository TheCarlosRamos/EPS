# CLAUDE.md — Buscador OSINT Automatizado

## Project Overview

Automated OSINT (Open Source Intelligence) search tool for the PCDF (Policia Civil do Distrito Federal), developed in partnership with UnB (Universidade de Brasilia). The system performs federated searches across public data sources, generates evidence-grade dossiers with SHA-256 hashing and chain-of-custody compliance, and enforces LGPD data protection requirements.

**Course:** Engenharia de Produto de Software (FGA0316) — 2026.1
**Organization:** FCTE-UNB-EPS5

## Tech Stack

- **Backend:** Python 3.12, FastAPI, Celery, Redis
- **Frontend:** React, TypeScript, Vite
- **Database:** PostgreSQL (metadata + audit), MinIO (evidence + dossiers)
- **Infrastructure:** Docker Compose, Nginx, HashiCorp Vault
- **CI/CD:** GitHub Actions (Ruff, Bandit, Safety, pytest + coverage)

## Repository Structure

```
.
├── .claude/                    # Claude Code configuration
│   ├── settings.json           # Shared project settings (committed)
│   ├── settings.local.json     # Personal settings (gitignored)
│   └── skills/
│       ├── code-review/        # /code-review — review against project standards
│       └── contributing/       # /contributing — commit, PR, and CI workflow guide
├── .github/workflows/
│   └── ci-quality.yml          # Ruff + Bandit + Safety + Tests & Coverage pipeline
├── backend/                    # Backend application (Celery + Redis queue system)
│   ├── pyproject.toml          # Backend deps, pytest, coverage, ruff config
│   ├── src/
│   │   ├── core/               # Celery app instance, configuration
│   │   └── queue/              # Decoupled queue module (retry, DLQ, health, monitoring)
│   └── tests/
│       ├── unit/               # Unit tests (no external services, fakeredis)
│       └── integration/        # Integration tests (requires Redis)
├── documentation/
│   ├── analysis/               # Project analysis (PRINCE2, PMBOK)
│   ├── diagrams/               # Architecture diagrams (Mermaid)
│   ├── secops/                 # Security operations config
│   │   └── pyproject.toml      # Ruff + Bandit + Safety configuration
│   └── specs/                  # Project specifications
├── src/                        # Application source code (legacy stub)
├── docker-compose.yml          # Dev/test services (Redis, PostgreSQL)
├── sonarqube_integration.md    # SonarCloud setup guide
└── CLAUDE.md                   # This file
```

## Code Quality Standards

### Python (Ruff)

Configuration: `documentation/secops/pyproject.toml`
- Target: Python 3.12
- Line length: 120
- Rules: E, F, W, I, N, S, B, A, C4, UP

```bash
# Lint
ruff check . --config documentation/secops/pyproject.toml

# Format
ruff format . --config documentation/secops/pyproject.toml

# Auto-fix
ruff check --fix . --config documentation/secops/pyproject.toml
```

### Security (Bandit)

Targets: `src/`, `backend/src/`, `workers/` (whichever exist)
Thresholds: severity >= medium, confidence >= medium

```bash
bandit -r src/ --severity-level medium --confidence-level medium
```

## Testing

Configuration: `backend/pyproject.toml`

```bash
# Unit tests only (no Docker required)
cd backend && python -m pytest tests/unit/ -m unit --cov=src --cov-report=term-missing

# Integration tests (requires Redis: docker compose up redis -d)
cd backend && python -m pytest tests/integration/ -m integration --cov=src --cov-report=term-missing

# Full suite with HTML + XML coverage reports
cd backend && python -m pytest --cov=src --cov-report=html --cov-report=xml --cov-report=term-missing
```

Coverage threshold: 60% (enforced in CI)

## Commit Convention

Conventional Commits v1.0.0 — https://www.conventionalcommits.org/en/v1.0.0/

Format: `<type>[(scope)]: <description>`

Types: `feat`, `fix`, `docs`, `chore`, `ci`, `refactor`, `perf`, `test`, `build`, `style`
Scopes: `api`, `frontend`, `workers`, `infra`, `docs`, `ci`

## Branch Naming

`<type>/<short-kebab-description>`

Types: `feat/`, `fix/`, `chore/`, `docs/`, `ci/`, `refactor/`

## Security Requirements

- SHA-256 for all evidence hashing (CPP Art. 158-B compliance)
- No hardcoded secrets — use environment variables or Vault
- No `eval`/`exec`/`pickle` with external data
- No `shell=True` in subprocess calls
- Parameterized SQL only (SQLAlchemy bind parameters)
- LGPD data minimization and retention policies
- Audit logging on all search operations

## Skills

- `/code-review` — Review code changes against project standards, security, and LGPD compliance
- `/contributing` — Guide for commits, PRs, branch naming, and CI troubleshooting

## Agents

- `secops-reviewer` — Security-focused PR reviewer: checks hardcoded secrets, container security, TLS, evidence hashing (SHA-256/CPP Art. 158), audit logging, LGPD compliance, and dependency vulnerabilities
