from fastapi import FastAPI
from src.api.v1 import health

app = FastAPI(
    title="RAG Module API",
    description="API for the OSINT Automated Search RAG module.",
    version="0.1.0"
)

app.include_router(health.router, prefix="/api/v1")

@app.get("/")
def root():
    return {"message": "Welcome to the RAG Module API. Use /api/v1/health to check dependencies."}
