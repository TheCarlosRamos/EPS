# SonarQube Community Edition - Integration Guide

This document describes the manual steps required to fully integrate SonarQube CE into the project CI/CD pipeline.

---

## 1. Deploy SonarQube CE (Self-Hosted)

Create `infra/docker-compose.sonarqube.yml`:

```yaml
services:
  sonarqube:
    image: sonarqube:lts-community
    container_name: sonarqube
    depends_on:
      sonar-db:
        condition: service_healthy
    ports:
      - "9000:9000"
    environment:
      SONAR_JDBC_URL: jdbc:postgresql://sonar-db:5432/sonarqube
      SONAR_JDBC_USERNAME: sonarqube
      SONAR_JDBC_PASSWORD: sonarqube
    volumes:
      - sonarqube_data:/opt/sonarqube/data
      - sonarqube_extensions:/opt/sonarqube/extensions
      - sonarqube_logs:/opt/sonarqube/logs
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:9000/api/system/status | grep -q UP"]
      interval: 30s
      timeout: 10s
      retries: 5

  sonar-db:
    image: postgres:16-alpine
    container_name: sonar-db
    environment:
      POSTGRES_USER: sonarqube
      POSTGRES_PASSWORD: sonarqube
      POSTGRES_DB: sonarqube
    volumes:
      - sonar_postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U sonarqube"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  sonarqube_data:
  sonarqube_extensions:
  sonarqube_logs:
  sonar_postgres_data:
```

Start SonarQube:

```bash
docker compose -f infra/docker-compose.sonarqube.yml up -d
```

Access at `http://localhost:9000` (default credentials: `admin` / `admin`). **Change the password on first login.**

---

## 2. Create Project & Generate Token

1. Log in to SonarQube at `http://localhost:9000`
2. Go to **Projects > Create Project > Manually**
3. Set:
   - **Project display name:** `Buscador OSINT Automatizado`
   - **Project key:** `buscador-osint-automatizado`
   - **Main branch name:** `main`
4. Go to **My Account > Security > Generate Tokens**
5. Create a token:
   - **Name:** `github-actions-ci`
   - **Type:** Project Analysis Token
   - **Project:** `buscador-osint-automatizado`
   - **Expires in:** 90 days (or as per your policy)
6. **Copy the token** (you won't see it again)

---

## 3. Add GitHub Actions Secrets

Go to the repository settings: **Settings > Secrets and variables > Actions > New repository secret**

Add two secrets:

| Secret Name | Value |
|---|---|
| `SONAR_TOKEN` | The token generated in step 2 |
| `SONAR_HOST_URL` | Your SonarQube server URL (e.g., `http://your-server:9000`) |

> **Note:** If using a self-hosted SonarQube, your server must be accessible from GitHub Actions runners. For a local-only setup, consider using a tunnel (e.g., ngrok) or deploying SonarQube to a cloud VM.

---

## 4. Create `sonar-project.properties`

Create this file at the repository root:

```properties
sonar.projectKey=buscador-osint-automatizado
sonar.projectName=Buscador OSINT Automatizado
sonar.projectVersion=0.1.0

# Source directories (update as project grows)
sonar.sources=backend/src,workers
sonar.tests=backend/tests

# Exclusions
sonar.exclusions=**/tests/**,**/__pycache__/**,**/node_modules/**,**/migrations/**,**/*.min.js,**/dist/**

# Python-specific
sonar.python.version=3.12

# Coverage (when tests are added)
sonar.python.coverage.reportPaths=coverage.xml

# Encoding
sonar.sourceEncoding=UTF-8
```

---

## 5. Configure Quality Gate

In SonarQube UI: **Quality Gates > Create**

Create a custom quality gate named `Buscador OSINT` with these conditions:

| Metric | Operator | Value |
|---|---|---|
| Coverage on New Code | is less than | 60% |
| Duplicated Lines on New Code | is greater than | 10% |
| Security Hotspots Reviewed on New Code | is less than | 100% |
| Reliability Rating on New Code | is worse than | A |
| Security Rating on New Code | is worse than | A |

Then set it as default for the project:
- Go to **Projects > Buscador OSINT Automatizado > Project Settings > Quality Gate**
- Select `Buscador OSINT`

### Enable Secret Detection

1. Go to **Administration > Configuration > General Settings > Secrets**
2. Ensure "Detect secrets" is **enabled**
3. Go to **Quality Profiles > Python** and verify that security rules (S6290, S6418, etc.) are active

---

## 6. Update Branch Ruleset (After First Successful Run)

Once SonarQube is running and the CI has executed at least one successful SonarQube Analysis, update the branch protection ruleset to require the SonarQube check:

```bash
# Get the current ruleset ID
RULESET_ID=$(gh api repos/FCTE-UNB-EPS5/buscador-osint-automatizado-eps_2026_1_grupo_1/rulesets --jq '.[0].id')

# Update the ruleset to add SonarQube as a required status check
gh api repos/FCTE-UNB-EPS5/buscador-osint-automatizado-eps_2026_1_grupo_1/rulesets/$RULESET_ID \
  --method PUT \
  --input - <<'EOF'
{
  "name": "Main branch protection",
  "enforcement": "active",
  "conditions": {
    "ref_name": {
      "include": ["refs/heads/main"],
      "exclude": []
    }
  },
  "bypass_actors": [
    {
      "actor_id": 62910920,
      "actor_type": "User",
      "bypass_mode": "always"
    }
  ],
  "rules": [
    {
      "type": "pull_request",
      "parameters": {
        "required_approving_review_count": 1,
        "dismiss_stale_reviews_on_push": true,
        "require_code_owner_review": false,
        "require_last_push_approval": false,
        "required_review_thread_resolution": true,
        "automatic_copilot_review_enabled": false
      }
    },
    {
      "type": "required_status_checks",
      "parameters": {
        "strict_required_status_checks_policy": true,
        "required_status_checks": [
          { "context": "Ruff Lint & Format Check" },
          { "context": "Bandit Security Scan" },
          { "context": "Safety Dependency Check" },
          { "context": "SonarQube Analysis" }
        ]
      }
    },
    {
      "type": "non_fast_forward"
    }
  ]
}
EOF
```

---

## 7. Verify Integration

After completing all steps above:

1. Create a test PR with a Python file
2. Check that the `SonarQube Analysis` job appears in the PR checks
3. Verify the Quality Gate result appears as a PR comment (if webhook is configured) or in the SonarQube dashboard
4. Confirm that a failing Quality Gate blocks the PR merge
