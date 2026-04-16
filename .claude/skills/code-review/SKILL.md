---
name: code-review
description: Review code changes against the Buscador OSINT project's coding standards, security requirements, and LGPD compliance patterns. Use when reviewing PRs, diffs, or any code changes.
user-invocable: true
allowed-tools: Read Glob Grep Bash(ruff *) Bash(bandit *) Bash(git diff *) Bash(git log *)
---

# Code Review — Buscador OSINT Automatizado

Review code changes against this project's enforced standards. Run automated checks first, then perform manual pattern analysis.

## Step 1: Identify Changes

Determine what is being reviewed:

```bash
# Changes in latest commit
git diff --name-only HEAD~1..HEAD

# Changes in PR branch vs main
git diff --name-only main...HEAD
```

Read every changed file. Understand the purpose of the change before reviewing.

## Step 2: Run Automated Checks

Run the same checks as CI and report results:

```bash
# Lint check
ruff check . --config documentation/secops/pyproject.toml

# Format check
ruff format --check . --config documentation/secops/pyproject.toml

# Security scan
TARGETS=""
for dir in src backend/src workers documentation/secops/src; do
  if [ -d "$dir" ]; then TARGETS="$TARGETS $dir"; fi
done
bandit -r $TARGETS --severity-level medium --confidence-level medium
```

If any check fails, report exact errors and provide auto-fix commands before proceeding.

## Step 3: Ruff Rule Enforcement

Project config: `target-version = "py312"`, `line-length = 120`
Reference: https://docs.astral.sh/ruff/rules/

| Category | Source | What It Catches | Key Violations |
|----------|--------|----------------|----------------|
| **E** | pycodestyle errors | Line length >120, indentation, syntax | E501 line too long, E711 comparison to None |
| **F** | Pyflakes | Unused imports, undefined names | F401 unused import, F811 redefined name |
| **W** | pycodestyle warnings | Trailing whitespace, blank lines | W291 trailing whitespace, W292 no newline at EOF |
| **I** | isort | Import sorting: stdlib > third-party > local | I001 unsorted imports |
| **N** | pep8-naming | snake_case functions, CapWords classes, ALL_CAPS constants | N801 class not CapWords, N802 function not lowercase |
| **S** | flake8-bandit | Security: assert, exec, hardcoded passwords | S101 assert used, S105 hardcoded password, S307 eval |
| **B** | flake8-bugbear | Mutable defaults, loop variable capture | B006 mutable default arg, B023 loop variable in closure |
| **A** | flake8-builtins | Shadowing Python builtins | A001 variable shadows builtin |
| **C4** | flake8-comprehensions | Unnecessary comprehension patterns | C400 unnecessary generator in list() |
| **UP** | pyupgrade | Modern Python 3.12 syntax | UP006 use `type` not `Type`, UP007 use `X | Y` for Union |

Flag violations even if automated checks pass when the spirit of the rule is violated.

## Step 4: Bandit Security Checks

Reference: https://bandit.readthedocs.io/en/latest/plugins/index.html

| ID | What | Correct Pattern |
|----|------|-----------------|
| B101 | `assert` in production | `if not condition: raise ValueError(...)` |
| B102 | `exec()` usage | Refactor to avoid exec entirely |
| B105 | Hardcoded passwords | Use env vars or HashiCorp Vault |
| B106 | Hardcoded password default arg | Require explicit parameter, no defaults |
| B301 | `pickle` usage | Use `json` or `msgpack` |
| B303 | MD5/SHA1 hashing | Use `hashlib.sha256()` (required for evidence in this project) |
| B307 | `eval()` usage | Use `ast.literal_eval()` or explicit parsing |
| B602 | `subprocess` with `shell=True` | `subprocess.run(["cmd", "arg"], shell=False)` |
| B608 | SQL via string formatting | SQLAlchemy bind parameters |

Suppression with `# nosec` is allowed only with a comment explaining why.

## Step 5: FastAPI Best Practices

Reference: https://github.com/zhanymkanov/fastapi-best-practices

**Routing and async:**
- `async def` ONLY for non-blocking I/O (async DB driver, httpx, aiofiles)
- `def` (sync) for CPU-bound or synchronous library calls — FastAPI runs these in a threadpool
- Never call `requests.get()` or blocking I/O inside an `async def` route

**Pydantic validation:**
- All request/response bodies use Pydantic models
- Use `Field()` with constraints: `Field(min_length=1, max_length=255)`, `Field(ge=0)`
- Validate CPF, email, phone with custom validators
- Split settings by domain: `DatabaseSettings`, `RedisSettings`, `VaultSettings`

**Dependency injection:**
- Use `Depends()` for auth, DB sessions, rate limiting
- Never instantiate services inside route handlers
- `BackgroundTasks` only for <1s tasks; Celery for anything longer

**Module structure:**
- Feature-based: `src/auth/`, `src/search/`, `src/dossier/`, `src/evidence/`
- Each module: `router.py`, `schemas.py`, `models.py`, `service.py`, `dependencies.py`
- No cross-feature imports; use shared services

**Testing:**
- `httpx.AsyncClient` with `ASGITransport` for async endpoint tests
- `app.dependency_overrides` for mocking

## Step 6: React/TypeScript Patterns

For frontend code, check:

- TypeScript strict mode — no `any` types without justification
- Component props defined with interfaces, not inline types
- API calls through a centralized service layer, not inline `fetch`
- No hardcoded API URLs — use environment variables (`VITE_API_URL`)
- Error boundaries for component trees handling API data
- No secrets, tokens, or API keys in frontend code (visible to users)

## Step 7: Security Patterns (OSINT-Specific)

This project handles law enforcement data. Apply heightened security review.

**Absolute prohibitions:**
- NO hardcoded secrets, tokens, passwords, or API keys in source code
- NO `eval()`, `exec()`, or `compile()` with user input
- NO `subprocess` with `shell=True`
- NO `pickle` for data from external sources
- NO MD5 or SHA1 — this project requires SHA-256 for evidence integrity (CPP Art. 158-B)
- NO SQL queries with string formatting or f-strings
- NO `.env` files committed (verify `.gitignore`)

**Required patterns:**
- Evidence files hashed with SHA-256 at moment of capture
- Database queries use parameterized statements (SQLAlchemy bind params)
- Secrets from env vars or HashiCorp Vault only
- API endpoints with personal data must have auth + RBAC checks
- Audit logging: every search records agent ID, inquiry number, timestamp, parameters
- TLS 1.3 for all internal service communication in production

## Step 8: LGPD Compliance Patterns

LGPD (Lei 13.709/2018) applies. Art. 4, III exempts security activities, but the exemption is not absolute.

**Code-level checks:**
- **Data minimization (Art. 6, III):** Scrapers collect only investigation-relevant data, not everything from a source
- **Retention policy (Art. 16):** Code storing personal data has TTL/expiration logic; no indefinite storage
- **Audit trail (Art. 37):** Every operation on personal data is logged (who, when, what, why)
- **Access control:** Routes with personal data enforce RBAC — investigators cannot access others' searches
- **Data deletion:** Functionality to purge data when investigation archived without charges (Art. 18)
- **Purpose limitation:** Search parameters tied to inquiry/procedure number; no ad-hoc searches without justification

**Review personal data handling in:**
- Search input validation (CPF, name, email, phone — all PII)
- Search result storage and display
- Dossier generation and retention
- Evidence capture and storage
- Audit log content (logs contain PII)

## Step 9: Produce Review Report

Structure the review as:

1. **Summary:** One paragraph on the changes and their purpose
2. **Automated results:** Pass/fail for ruff lint, ruff format, bandit
3. **Issues found:**
   - **BLOCKER** — Must fix before merge (security vulnerabilities, CI failures, data leaks)
   - **WARNING** — Should fix (code quality, missing validation)
   - **SUGGESTION** — Nice to have (performance, readability, modern syntax)
4. **LGPD considerations:** Any personal data handling concerns
5. **Auto-fix commands:**
   ```bash
   ruff check --fix . --config documentation/secops/pyproject.toml
   ruff format . --config documentation/secops/pyproject.toml
   ```
