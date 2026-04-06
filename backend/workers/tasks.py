from celery import Celery
from core.intent import parse_intent
from core.aggregator import aggregate
from core.registry import register, all_scrapers
from scrapers.google.scraper import GoogleScraper
from scrapers.instagram.scraper import InstagramScraper
from scrapers.jusbrasil.scraper import JusbrasilScraper
from audit.logger import log
from evidence.snapshot import capture
from analysis.inference import infer
from analysis.timeline import build
import os, time

app = Celery('osint', broker='redis://redis:6379/0')

register(GoogleScraper())
register(InstagramScraper())
register(JusbrasilScraper())

@app.task
def run_search(query: str, user_data: dict = None):
    intent = parse_intent(query)
    results = {}
    
    # Log de auditoria
    log({'action': 'search_started', 'query': query, 'user': user_data, 'intent': intent})
    
    for scraper in all_scrapers():
        try:
            print(f"Running scraper: {scraper.name}")
            scraper_results = scraper.search(intent)
            print(f"Scraper {scraper.name} returned {len(scraper_results)} results")
            results[scraper.name] = scraper_results
            
            # Captura de evidências desabilitada temporariamente
            # TODO: Implementar com Playwright quando disponível
            for item in scraper_results[:3]:
                item['evidence'] = "disabled_temporarily"
                item['ts'] = int(time.time())
                    
        except Exception as e:
            print(f"Scraper {scraper.name} error: {str(e)}")
            results[scraper.name] = []
            log({'action': 'scraper_error', 'scraper': scraper.name, 'error': str(e)})
    
    aggregated = aggregate(results)
    
    # Análise de inteligência
    graph_data = infer(aggregated)
    timeline_data = build(aggregated)
    
    log({'action': 'search_completed', 'query': query, 'results_count': len(aggregated)})
    
    final_result = {
        'results': aggregated,
        'graph': graph_data,
        'timeline': timeline_data
    }
    
    # Armazenar no Redis para cache
    try:
        import redis
        r = redis.Redis(host='redis', port=6379, db=0)
        r.setex(f"task:{run_search.request.id}", 3600, str(final_result))  # 1 hora expira
        print(f"Stored result in Redis for task {run_search.request.id}")
    except Exception as e:
        print(f"Could not store in Redis: {e}")
    
    return final_result
