# SonarCloud Integration Guide

This document describes the manual steps required to integrate SonarCloud (cloud-hosted SonarQube) into the project CI/CD pipeline. SonarCloud is free for open-source projects and requires no self-hosted infrastructure.

---

## 1. Sign Up & Import Repository

1. Go to [sonarcloud.io](https://sonarcloud.io) and click **Log in with GitHub**
2. Authorize SonarCloud to access your GitHub account
3. Click **Import an organization from GitHub**
4. Select the organization **FCTE-UNB-EPS5**
5. Choose the **Free plan** (available for public repositories)
6. Click **Import organization**
7. On the next screen, select the repository **buscador-osint-automatizado-eps_2026_1_grupo_1**
8. Click **Set Up** to create the SonarCloud project

After import, note your:
- **Organization key:** `fcte-unb-eps5` (lowercase, visible in SonarCloud URL)
- **Project key:** will be shown on the project setup page (e.g., `FCTE-UNB-EPS5_buscador-osint-automatizado-eps_2026_1_grupo_1`)

---

## 2. Generate a Token

1. In SonarCloud, go to **My Account > Security** (click your avatar top-right > My Account > Security tab)
2. Under **Generate Tokens**:
   - **Name:** `github-actions-ci`
   - **Type:** Project Analysis Token
   - **Expires in:** 90 days (or as per your policy)
3. Click **Generate**
4. **Copy the token** (you won't see it again)

---

## 3. Add GitHub Actions Secret

Go to the repository: **Settings > Secrets and variables > Actions > New repository secret**

| Secret Name | Value |
|---|---|
| `SONAR_TOKEN` | The token generated in step 2 |

> **Note:** No `SONAR_HOST_URL` is needed — the SonarCloud action automatically uses `https://sonarcloud.io`.

---

## 4. Create `sonar-project.properties`

Create this file at the repository root:

```properties
sonar.organization=fcte-unb-eps5
sonar.projectKey=FCTE-UNB-EPS5_buscador-osint-automatizado-eps_2026_1_grupo_1
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

> **Important:** Update `sonar.organization` and `sonar.projectKey` with the actual values shown in your SonarCloud project settings if they differ from the above.

---

## 5. Configure Quality Gate

SonarCloud comes with the **"Sonar way"** default quality gate which is already good. To customize:

1. In SonarCloud, go to **Organization Settings > Quality Gates**
2. Click **Create** to create a custom quality gate named `Buscador OSINT`
3. Add these conditions:

| Metric | Operator | Value |
|---|---|---|
| Coverage on New Code | is less than | 60% |
| Duplicated Lines on New Code | is greater than | 10% |
| Security Hotspots Reviewed on New Code | is less than | 100% |
| Reliability Rating on New Code | is worse than | A |
| Security Rating on New Code | is worse than | A |

4. Go to **Project Settings > Quality Gate** and select `Buscador OSINT`

### PR Decoration (Automatic)

SonarCloud automatically decorates pull requests with analysis results (comments showing quality gate status, new issues, coverage). This works out of the box once the GitHub App is authorized.

---

## 6. Update Branch Ruleset (After First Successful Run)

Once SonarCloud has run successfully at least once, add it as a required status check:

```bash
# Get the current ruleset ID
RULESET_ID=$(gh api repos/FCTE-UNB-EPS5/buscador-osint-automatizado-eps_2026_1_grupo_1/rulesets --jq '.[0].id')

# Update the ruleset to add SonarCloud as a required status check
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
        "required_review_thread_resolution": true
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
          { "context": "SonarCloud Analysis" }
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
