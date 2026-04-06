
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from api.schemas import SearchRequest
from workers.tasks import run_search
from auth import get_current_user
from models import Investigacao
from pdf_service import gerar_pdf
import jwt
import time

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
        # Verificar se temos o resultado armazenado
        if task_id in task_results:
            return {"task_id": task_id, "status": "SUCCESS", "result": task_results[task_id]}
        
        # Tentar obter do Celery (com fallback)
        from celery.result import AsyncResult
        result = AsyncResult(task_id, app=run_search.app)
        
        if result.state == 'SUCCESS':
            # Armazenar resultado para consultas futuras
            task_results[task_id] = result.result
            return {"task_id": task_id, "status": "SUCCESS", "result": result.result}
        elif result.state == 'PENDING':
            return {"task_id": task_id, "status": "PENDING"}
        elif result.state == 'FAILURE':
            return {"task_id": task_id, "status": "FAILURE", "error": str(result.info)}
        else:
            return {"task_id": task_id, "status": result.state}
            
    except Exception as e:
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
