---
name: contributing
description: Guide for contributing to the Buscador OSINT project — commit standards (Conventional Commits), branch naming, PR workflow, CI pipeline interpretation, and auto-fix commands for common failures.
user-invocable: true
allowed-tools: Read Glob Grep Bash(git *) Bash(gh *) Bash(ruff *) Bash(bandit *)
---

# Contributing — Buscador OSINT Automatizado

Complete guide for the contribution workflow: branching, committing, creating PRs, and resolving CI failures.

## 1. Branch Naming Convention

```
<type>/<short-description>
```

| Type | When to Use | Example |
|------|-------------|---------|
| `feat/` | New feature or capability | `feat/cpf-search-endpoint` |
| `fix/` | Bug fix | `fix/scraper-timeout-handling` |
| `chore/` | Maintenance, dependencies, tooling | `chore/upgrade-ruff-config` |
| `docs/` | Documentation only | `docs/api-authentication-guide` |
| `ci/` | CI/CD pipeline changes | `ci/add-sonarcloud-step` |
| `refactor/` | Code restructuring, no behavior change | `refactor/extract-search-service` |

Rules:
- Lowercase with hyphens (kebab-case)
- Under 50 characters total
- Always branch from `main`:

```bash
git checkout main && git pull origin main && git checkout -b feat/my-feature
```

## 2. Commit Message Standards

This project follows **Conventional Commits v1.0.0**.
Reference: https://www.conventionalcommits.org/en/v1.0.0/

### Format

```
<type>[(scope)]: <description>

[optional body]

[optional footer(s)]
```

### Types

| Type | Semver | When to Use |
|------|--------|-------------|
| `feat` | MINOR | New feature visible to users |
| `fix` | PATCH | Bug fix |
| `docs` | — | Documentation only |
| `chore` | — | Maintenance (deps, configs, tooling) |
| `ci` | — | CI/CD pipeline changes |
| `refactor` | — | Code change that neither fixes nor adds |
| `perf` | PATCH | Performance improvement |
| `test` | — | Adding or correcting tests |
| `build` | — | Build system or external dependencies |
| `style` | — | Formatting, whitespace (no logic change) |

### Scopes

| Scope | Covers |
|-------|--------|
| `api` | FastAPI backend — routes, schemas, services |
| `frontend` | React/TypeScript frontend |
| `workers` | Celery workers, scrapers, task processing |
| `infra` | Docker, Docker Compose, Nginx, deployment |
| `docs` | Documentation files |
| `ci` | GitHub Actions workflows |

### Examples

```
feat(api): add CPF search endpoint with Pydantic validation

fix(workers): handle timeout in social media scraper gracefully

docs(api): document authentication flow and RBAC endpoints

chore(infra): upgrade PostgreSQL from 15 to 16 in docker-compose

ci: add SonarCloud analysis step to quality pipeline

refactor(api): extract evidence hashing into shared service

perf(workers): batch database inserts for scraper results

test(api): add integration tests for dossier generation

feat(api)!: change search response format to include pagination

BREAKING CHANGE: Search endpoint now returns paginated results.
The results field is wrapped in a data object with total, page,
and page_size fields.
```

### Rules

- Subject: imperative mood, lowercase first letter, no period, max 72 characters
- Body: explain **why**, not **what** (the diff shows what)
- One logical change per commit
- Reference issues in footer: `Closes #42` or `Refs #42`

### Breaking Changes

Add `!` after type/scope: `feat(api)!: redesign search response schema`
Or use a `BREAKING CHANGE:` footer.

## 3. Pull Request Workflow

### Creating a PR

```bash
git push -u origin feat/my-feature

gh pr create --title "feat(api): add CPF search endpoint" --body "$(cat <<'EOF'
## Summary
- Add new `/api/v1/search/cpf` endpoint
- Validate CPF format using custom Pydantic validator
- Queue search task via Celery for async processing

## Changes
- `src/search/router.py` — new route handler
- `src/search/schemas.py` — CPF request/response models
- `src/search/service.py` — search orchestration logic

## Testing
- [ ] Unit tests pass
- [ ] Integration test for endpoint
- [ ] Manual test with sample data

## Security Considerations
- CPF is PII — validated but not logged in plain text
- Search requires authentication and inquiry number

Closes #42
EOF
)"
```

### PR Title Format

Same as commit messages: `<type>[(scope)]: <short description>`

### PR Description — Required Sections

1. **Summary** — 1-3 bullet points (what and why)
2. **Changes** — List of files changed and what was done
3. **Testing** — Checklist of how changes were verified
4. **Security Considerations** — Any security implications (required for this project)
5. **Issue reference** — `Closes #N` or `Refs #N`

### PR Merge Requirements

Branch protection enforces:
- At least **1 approving review**
- All **review comments resolved**
- All **CI status checks pass** (Ruff, Bandit, Safety)
- Stale reviews dismissed on new pushes

## 4. Development Workflow

```
1. Branch    →  git checkout -b feat/my-feature
2. Code      →  (make changes)
3. Check     →  ruff check . --config documentation/secops/pyproject.toml
                ruff format --check . --config documentation/secops/pyproject.toml
                bandit -r src/ --severity-level medium --confidence-level medium
4. Fix       →  ruff check --fix . --config documentation/secops/pyproject.toml
                ruff format . --config documentation/secops/pyproject.toml
5. Commit    →  git add <files> && git commit -m "feat(api): description"
6. Push      →  git push -u origin feat/my-feature
7. PR        →  gh pr create ...
8. CI        →  gh pr checks <number>
9. Review    →  address feedback, commit, push
10. Merge    →  reviewer merges after approval + green CI
```

## 5. CI Pipeline — Interpreting Failures

Pipeline: `.github/workflows/ci-quality.yml`
Triggers: push to `main`, PRs targeting `main`

### Job 1: Ruff Lint & Format Check

**What runs:**
```bash
ruff check . --config documentation/secops/pyproject.toml
ruff format --check . --config documentation/secops/pyproject.toml
```

**Lint failure example:**
```
src/search/router.py:15:1: F401 `os` imported but unused
src/search/service.py:42:5: S105 Possible hardcoded password
```

**Format failure example:**
```
Would reformat: src/search/router.py
2 files would be reformatted
```

**How to fix:**
```bash
# Auto-fix lint (safe fixes)
ruff check --fix . --config documentation/secops/pyproject.toml

# Auto-format
ruff format . --config documentation/secops/pyproject.toml

# Unsafe fixes (review each one carefully)
ruff check --fix --unsafe-fixes . --config documentation/secops/pyproject.toml
```

Some issues cannot be auto-fixed (e.g., S105 hardcoded password) — these require manual changes.

### Job 2: Bandit Security Scan

**What runs:**
```bash
bandit -r <src-dirs> --severity-level medium --confidence-level medium
```

**Failure example:**
```
>> Issue: [B105:hardcoded_password_string] Possible hardcoded password: 'mysecret'
   Severity: Low   Confidence: Medium
   CWE: CWE-259
   Location: src/config.py:12:0
```

**How to fix:**
- Move secrets to environment variables or Vault
- Replace `assert` with proper error handling
- Replace `eval()`/`exec()` with safe alternatives
- Use `subprocess.run([...], shell=False)`
- Use `hashlib.sha256()` instead of md5/sha1

No auto-fix — all Bandit issues require manual code changes.

### Job 3: Safety Dependency Check

**What runs:**
```bash
cd documentation/secops && safety scan
```

**How to fix:** Upgrade vulnerable dependency in `pyproject.toml`, then `poetry lock`.

Currently runs with `continue-on-error: true` (non-blocking).

### Required Checks for Merge

| Check | GitHub Name | Blocking? |
|-------|------------|-----------|
| Ruff | `Ruff Lint & Format Check` | Yes |
| Bandit | `Bandit Security Scan` | Yes |
| Safety | `Safety Dependency Check` | No (continue-on-error) |

## 6. Auto-Fix Quick Reference

```bash
# Fix lint + format in one shot
ruff check --fix . --config documentation/secops/pyproject.toml && \
ruff format . --config documentation/secops/pyproject.toml

# Verify everything passes (dry run, no changes)
ruff check . --config documentation/secops/pyproject.toml && \
ruff format --check . --config documentation/secops/pyproject.toml && \
bandit -r src/ --severity-level medium --confidence-level medium
```

## 7. When Helping a Contributor

When a user asks for help contributing:

1. Ask what they want to accomplish (feature, fix, docs, etc.)
2. Help create the correct branch name
3. Guide through the changes
4. Run local checks before committing
5. Auto-fix what can be auto-fixed
6. Craft the commit message following Conventional Commits
7. Create the PR with correct title and description template
8. If CI fails, diagnose and fix the issues
