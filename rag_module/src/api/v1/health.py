import httpx
from fastapi import APIRouter
from src.config import settings

router = APIRouter()

@router.get("/health")
async def health_check():
    status = {
        "status": "ok",
        "neo4j": "unknown",
        "qdrant": "unknown",
        "redis": "unknown",
        "ollama": "unknown"
    }
    
    # Check Neo4j
    try:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(settings.NEO4J_URI, auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD))
        driver.verify_connectivity()
        status["neo4j"] = "ok"
        driver.close()
    except Exception as e:
        status["neo4j"] = f"error: {str(e)}"
        status["status"] = "error"

    # Check Qdrant
    try:
        from qdrant_client import QdrantClient
        client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)
        client.get_collections()
        status["qdrant"] = "ok"
    except Exception as e:
        status["qdrant"] = f"error: {str(e)}"
        status["status"] = "error"

    # Check Redis
    try:
        from redis import asyncio as aioredis
        redis = await aioredis.from_url(settings.REDIS_URL)
        await redis.ping()
        status["redis"] = "ok"
        await redis.aclose()
    except Exception as e:
        status["redis"] = f"error: {str(e)}"
        status["status"] = "error"

    # Check Ollama
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{settings.OLLAMA_BASE_URL}/api/tags")
            if resp.status_code == 200:
                models = resp.json().get("models", [])
                if any(m.get("name") == settings.LLM_MODEL_NAME for m in models):
                    status["ollama"] = "ok"
                else:
                    status["ollama"] = f"model {settings.LLM_MODEL_NAME} not loaded"
                    status["status"] = "warning"
            else:
                status["ollama"] = f"error: status code {resp.status_code}"
                status["status"] = "error"
    except Exception as e:
        status["ollama"] = f"error: {str(e)}"
        status["status"] = "error"

    return status
