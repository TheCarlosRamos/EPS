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
import os, time, json

redis_host = os.getenv('REDIS_HOST', 'localhost')
app = Celery('osint', broker=f'redis://{redis_host}:6379/0')

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
            if intent['type'] not in scraper.supported_types:
                print(f"Skipping scraper {scraper.name} for intent type {intent['type']}")
                continue
                
            print(f"Running scraper: {scraper.name}")
            scraper_results = scraper.search(intent)
            print(f"Scraper {scraper.name} returned {len(scraper_results)} results")
            results[scraper.name] = scraper_results
            
            # Captura de evidências (RF04) - Agora habilitado com Playwright
            for item in scraper_results[:3]:
                try:
                    if 'url' in item:
                        evidence_path = f"evidence_{int(time.time())}_{scraper.name}.png"
                        try:
                            # Captura real com Playwright
                            item['evidence'] = capture(item['url'], evidence_path)
                        except Exception as playwright_err:
                            print(f"Playwright not available: {playwright_err}, using placeholder")
                            item['evidence'] = "captured_snapshot_placeholder"
                    else:
                        item['evidence'] = "no_url_to_capture"
                    item['ts'] = int(time.time())
                except Exception as ex:
                    print(f"Evidence capture error: {ex}")
                    item['evidence'] = "capture_failed"
                    
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
    
    # Gerar Dossiê PDF Automático (RF05)
    try:
        from pdf_service import gerar_pdf
        dossie_data = {
            'id': run_search.request.id,
            'query': query,
            'tipo': intent['type'],
            'total_achados': len(aggregated),
            'data': time.strftime("%d/%m/%Y %H:%M:%S")
        }
        pdf_path = gerar_pdf(dossie_data)
        final_result['dossie_pdf'] = pdf_path
        print(f"Dossier generated: {pdf_path}")
    except Exception as e:
        print(f"PDF generation error: {e}")
    
    # Armazenar no Redis para cache
    try:
        import redis
        redis_host = os.getenv('REDIS_HOST', 'localhost')
        r = redis.Redis(host=redis_host, port=6379, db=0)
        # Serializar como JSON
        r.setex(f"task:{run_search.request.id}", 3600, json.dumps(final_result))  # 1 hora expira
        print(f"Stored result in Redis for task {run_search.request.id}")
    except Exception as e:
        print(f"Could not store in Redis: {e}")
    
    return final_result
