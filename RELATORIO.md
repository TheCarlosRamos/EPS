# 📘 Desafio 01: Onboarding SecOps & Soberania Técnica (Fase 1)

## 🎯 Objetivo

Estabelecer a infraestrutura base individual e a esteira de segurança (**Security Gate**), garantindo que cada engenheiro esteja apto a integrar os squads da PCDF com um ambiente padronizado e seguro.

---

## 1. 🧭 Contexto Estratégico

Alinhado ao **Domínio Oito do CISSP (Software Development Security)**, reforça-se que **segurança não é um estágio final**, mas um atributo intrínseco desde a primeira linha de código.  
Este domínio orienta que a proteção dos ativos digitais exige controles de segurança aplicados em todo o **SDLC**, prevenindo vulnerabilidades antes que o software entre em produção.

A disciplina adota a abordagem **AI‑First**, usando aceleradores como o **GitHub Copilot**, equilibrados pelo princípio da **Soberania Técnica**, aplicando:

- **Defesa em Profundidade**  
- **Fail-Safe (Falha Segura)**  
- **Sandboxing e Isolamento** com **Docker**  
- **Auditoria Contínua (SAST)** usando Bandit e Pydantic  

Essas práticas garantem operação segura em ambientes **on‑premise** da **PCDF**, mantendo resiliência e custódia da prova digital.

---

## 2. 🖥️ Setup Mandatório do Ambiente (Localhost)

Cada aluno deve configurar:

- **Python 3.12** (versões experimentais como 3.14 não devem ser usadas)  
- **Poetry** para gestão determinística de dependências  
- **Django 5.0+**  
- **Docker** para isolamento e futura orquestração de modelos locais  

---

## 3. 🔐 Esteira de Segurança (DevSecOps)

O repositório individual contém um workflow no **GitHub Actions** (`.github/workflows/security-gate.yml`) com:

| Controle | Ferramenta |
|----------|------------|
| SAST | Bandit |
| SCA | Safety |
| Linter / Formatter | Ruff |
| Secret scanning | Gitleaks |

---

## ✅ Produto Final: Relatório de Prontidão Técnica

### 1. Evidência de ambiente

Após `poetry install`, execute:

```bash
poetry config virtualenvs.in-project true
poetry env info
```

O pipeline imprime `poetry env info` em cada execução (job **Evidência de ambiente**), usando **Python 3.12** no runner `ubuntu-latest`.

### 2. Evidência de segurança (Bandit)

Execução local:

```bash
poetry run bandit -r .
```

Esperado: **nenhum issue** no código atual (`sample_app.py`). O relatório JSON é gerado no CI como artefato `bandit-report`.

### 3. Evidência de CI

- Aba **Actions** do repositório: workflow **Security Gate** em verde após push na branch padrão.  
- Badge (opcional): adicione no README após o primeiro run bem-sucedido.

### 4. Declaração de prontidão (remote)

Repositório remoto configurado para:

`https://github.com/TheCarlosRamos/EPS`

Para clonar ou sincronizar:

```bash
git clone https://github.com/TheCarlosRamos/EPS.git
cd EPS
poetry install
```

Migração futura para a organização (upstream) seguirá as instruções oficiais quando liberadas.

---

## 4. 🚀 Migração para a Organização **rmchaimalm**

A migração ocorrerá após liberação das ferramentas via **GitHub Global Campus for Teachers**, permitindo acesso a:

- GitHub Pro  
- GitHub Copilot  
- GitHub Advanced Security  

Após provisionamento da organização, serão fornecidas as instruções para configurar:

```bash
git remote add upstream <URL_OFICIAL>
```

Essa estratégia mantém rastreabilidade e preserva o histórico da Fase 1.

---

## 5. ✅ Checkpoint de Prontidão Técnica: Comandos e Prazos

### 📝 Resumo de Comandos (Checklist)

#### 1. Gestão de dependências e isolamento

```bash
poetry config virtualenvs.in-project true
poetry install
```

#### 2. Protocolo de auditoria e qualidade (Domínio 8 CISSP)

```bash
poetry run bandit -r .
poetry run ruff check .
poetry run ruff format --check .
poetry run safety scan
```

> **Safety (SCA):** a CLI 3.x exige autenticação. Obtenha uma chave em [Safety CLI](https://docs.safetycli.com/) e configure no repositório GitHub: **Settings → Secrets and variables → Actions → `SAFETY_API_KEY`**. Sem essa secret, o passo **SCA (Safety)** falha no CI.

### Prazos (referência do desafio)

| Marco | Data |
|-------|------|
| Prazo final | 30/03/2026 |
| Aula presencial | 01/04/2026 |

---

## 6. Configuração do CI (resumo técnico)

| Secret / variável | Uso |
|-------------------|-----|
| `SAFETY_API_KEY` | Obrigatória para o passo **SCA (Safety)** no GitHub Actions |
| `GITHUB_TOKEN` | Fornecida automaticamente; usada pelo Gitleaks |

Arquivo do workflow: `.github/workflows/security-gate.yml`.
