# RAG System Architecture — Graph + Vector + LLM

Reference: [Issue #11 — RAG Module](https://github.com/FCTE-UNB-EPS5/buscador-osint-automatizado-eps_2026_1_grupo_1/issues/11)

---

## Overview

The RAG (Retrieval-Augmented Generation) module is responsible for correlating entities, building a knowledge graph, and providing natural language explanations for links discovered during OSINT investigations. It prioritizes **data sovereignty** by using 100% locally-hosted AI models and infrastructure.

```
┌─────────────┐      ┌─────────────┐      ┌─────────────────┐
│  Data       │─────>│  Ingestion  │─────>│  Neo4j          │
│  Storage    │      │  Service    │      │  (Knowledge     │
│  (JSON)     │      │             │      │   Graph)        │
└─────────────┘      └──────┬──────┘      └─────────────────┘
                            │
               ┌────────────┴────────────┐
               │                         │
      ┌────────▼────────┐       ┌────────▼────────┐
      │  spaCy NER      │       │  Qdrant         │
      │  (Extraction)   │       │  (Vector DB)    │
      └────────┬────────┘       └────────┬────────┘
               │                         │
               └────────────┬────────────┘
                            │
      ┌─────────────────────▼─────────────────────┐
      │  Inference Engine (Rules + Graph)         │
      └─────────────────────┬─────────────────────┘
                            │
      ┌─────────────────────▼─────────────────────┐
      │  Ollama (LLM Explainer - Local)           │
      └─────────────────────┬─────────────────────┘
                            │
                     ┌──────▼──────┐
                     │  FastAPI    │
                     │  (Dossier)  │
                     └─────────────┘
```

---

## Module Structure

The RAG module follows a domain-driven structure isolated within the `rag_module` directory:

```
rag_module/
├── src/
│   ├── main.py              # FastAPI application instance
│   ├── config.py            # Pydantic Settings (Neo4j, Qdrant, Redis, Ollama)
│   ├── api/
│   │   ├── v1/              # Versioned API endpoints (dossie, vinculos, health)
│   │   └── deps.py          # Dependency injection
│   ├── db/
│   │   ├── neo4j_session.py # Driver management
│   │   └── qdrant_client.py # Client initialization
│   ├── schemas/
│   │   ├── output.py        # Pydantic models (DossieData, GraphData)
│   │   └── enums.py         # Type definitions (EntityTypes, LinkTypes)
│   └── services/
│       ├── ingestion/       # Loading and chunking logic
│       ├── extraction/      # spaCy NER and pattern matching
│       ├── graph/           # Neo4j schema and builder logic
│       ├── inference/       # Link inference rules and scoring
│       ├── llm/             # Ollama client and prompt templates
│       └── dossie/          # Aggregation logic
└── tests/                   # Test suite (Unit & Integration)
```

---

## Components

### Configuration (`src/config.py`)

Uses `Pydantic Settings` to load environment variables. Key sections include:

| Category | Variables | Description |
|---|---|---|
| **Neo4j** | `NEO4J_URI`, `NEO4J_USER` | Connection to the Graph database |
| **Qdrant** | `QDRANT_HOST`, `QDRANT_PORT` | Connection to the Vector database |
| **Ollama** | `OLLAMA_BASE_URL`, `LLM_MODEL_NAME` | Connection to the local LLM instance |
| **Models** | `EMBEDDING_MODEL_NAME` | MiniLM model for semantic search |

### Ingestion & Extraction (`services/ingestion/`, `services/extraction/`)

- **Chunking:** Semantic splitting of text data for vector storage.
- **NER (spaCy):** Extracts entities (People, Orgs, Locations) using `pt_core_news_lg` and custom rules for police-specific terminology (vulgos, factions).

### Knowledge Graph (`services/graph/`, `services/inference/`)

- **Storage (Neo4j):** Stores structured relations with Cypher-pure queries.
- **Inference Engine:** Implements RF06 (Link Inference) using deterministic rules:
  - **Co-occurrence:** Entities appearing in the same documents.
  - **Short Path:** 2nd and 3rd-degree connections.
  - **Common Context:** Same organizations or locations.
- **Scoring:** Aggregates rule hits into a 0.0-1.0 confidence score.

### LLM Explainer (`services/llm/`)

- **Ollama:** Wraps the local `llama3.1:8b` model.
- **Responsibility:** **Only** generates natural language explanations for discovered links. It does NOT decide on the existence of the link.
- **Data Safety:** Context is limited to the top-K relevant chunks from Qdrant.

### API & Dossier (`api/v1/`, `services/dossie/`)

- **`/dossie/{alvo_id}`:** Compiles all findings into a structured Pydantic object containing the target info, related entities, timeline, and link explanations.
- **`/health`:** Active probe of all 4 dependent services (Neo4j, Qdrant, Redis, Ollama).

---

## Setup

### Prerequisites

- Python 3.12+
- Poetry
- Docker and Docker Compose

### 1. Start Support Services

```bash
cd rag_module
docker-compose up -d
```

Starts Neo4j (7474), Qdrant (6333), Redis (6380), and Ollama (11434).

### 2. Install Dependencies

```bash
poetry install
```

### 3. Start API

```bash
poetry run uvicorn src.main:app --reload
```

---

## Testing

### Structure

```
rag_module/tests/
├── unit/           # Logic testing with mocks
└── integration/    # Testing against real Neo4j/Qdrant containers
```

### Running Tests

```bash
cd rag_module
poetry run pytest
```

---

## Security & Privacy (LGPD)

- **Soberana Total:** No data leaves the local infrastructure. No external API calls to OpenAI/Anthropic.
- **Data Minimization:** PII masking (e.g., CPF) before graph visualization where applicable.
- **Chain of Custody:** Metadata in Neo4j and Qdrant includes the source document SHA-256 for evidence integrity.
- **Traceability:** LLM explanations are clearly marked as AI-generated and include the source chunks used as evidence.