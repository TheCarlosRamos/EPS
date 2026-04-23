
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from api.schemas import SearchRequest
from workers.tasks import run_search
from auth import get_current_user
from models import Investigacao
from pdf_service import gerar_pdf
import jwt
import time
import os
import json

app = FastAPI(title="OSINT Automatizado – PCDF")

# Adicionar middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "OSINT PCDF API", "version": "1.0.0"}

@app.post("/login")
def login():
    """Endpoint para gerar token de desenvolvimento"""
    payload = {
        "sub": "pcdf_user",
        "name": "Usuário PCDF",
        "iat": int(time.time()),
        "exp": int(time.time()) + 3600  # 1 hora
    }
    token = jwt.encode(payload, "pcdf-secret", algorithm="HS256")
    return {"access_token": token, "token_type": "bearer"}

@app.post("/search")
def search(req: SearchRequest, user=Depends(get_current_user)):
    task = run_search.delay(req.query, user)
    return {"task_id": task.id, "user": user}

@app.post('/investigacoes')
def criar(inv: Investigacao, user=Depends(get_current_user)):
    pdf=gerar_pdf(inv.dict())
    return {'status':'ok','pdf':pdf,'user':user}

# Storage simples para resultados (em produção usar Redis/DB)
task_results = {}

@app.get("/task/{task_id}")
def get_task_status(task_id: str):
    try:
        print(f"Checking task status for: {task_id}")
        
        # Tentar buscar do Redis cache
        try:
            import redis
            redis_host = os.getenv('REDIS_HOST', 'localhost')
            r = redis.Redis(host=redis_host, port=6379, db=0)
            cached_result = r.get(f"task:{task_id}")
            if cached_result:
                print(f"Found in Redis cache")
                # Parsear JSON para dicionário
                result_dict = json.loads(cached_result.decode('utf-8'))
                return {"task_id": task_id, "status": "SUCCESS", "result": result_dict}
        except Exception as e:
            print(f"Redis cache error: {e}")
        
        # Se não está no cache, verificar se está em processamento
        print(f"Task {task_id} not found in cache, status PENDING")
        return {"task_id": task_id, "status": "PENDING"}
            
    except Exception as e:
        print(f"ERROR in get_task_status: {str(e)}")
        return {"task_id": task_id, "status": "ERROR", "error": str(e)}

@app.get("/tasks")
def list_tasks():
    """Listar todas as tasks para debug"""
    from celery.result import AsyncResult
    # Esta é uma função de debug - em produção remover
    return {"message": "Endpoint para debug de tasks"}

@app.get("/debug")
def debug_simple():
    """Debug simples"""
    return {"message": "debug working", "scrapers": ["google", "instagram", "jusbrasil"]}

@app.get("/debug/scrapers")
def debug_scrapers():
    """Testar scrapers individualmente"""
    from core.intent import parse_intent
    from core.registry import all_scrapers
    
    test_query = "gabrielmod342@gmail.com"
    intent = parse_intent(test_query)
    
    results = {}
    for scraper in all_scrapers():
        try:
            scraper_results = scraper.search(intent)
            results[scraper.name] = {
                "status": "success",
                "count": len(scraper_results),
                "data": scraper_results[:2]  # Primeiros 2 resultados
            }
        except Exception as e:
            results[scraper.name] = {
                "status": "error",
                "error": str(e)
            }
    
    return {"query": test_query, "scrapers": results}
