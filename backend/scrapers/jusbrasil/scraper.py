import requests
import random
import os
from bs4 import BeautifulSoup
from scrapers.base import BaseScraper

class JusbrasilScraper(BaseScraper):
    name = 'jusbrasil'
    supported_types = ["NAME", "CPF"]
    
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
    ]
    
    def search(self, intent):
        q = intent['value']
        url = f'https://www.jusbrasil.com.br/busca?q={q}'
        
        # Suporte a proxy para anonimato (RNF01)
        proxy = os.getenv('HTTP_PROXY')
        proxies = {'http': proxy, 'https': proxy} if proxy else None
        
        try:
            headers = {
                "User-Agent": random.choice(self.USER_AGENTS),
                "Accept-Language": "pt-BR,pt;q=0.9",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
            }
            r = requests.get(url, headers=headers, timeout=10, proxies=proxies)
            print(f"[JusbrasilScraper] Status: {r.status_code}, Content length: {len(r.text)}")
            
            soup = BeautifulSoup(r.text, 'html.parser')
            res = []
            
            # Múltiplos seletores para encontrar resultados
            selectors = [
                'a.resultado-busca-link',           # Seletor original
                'a[href*="/busca/"]',               # Links de busca
                'div.container-resultado a',        # Container padrão
                'a[data-testid*="resultado"]',      # Com data-testid
                'a',                                # Fallback: todos os links
            ]
            
            found_results = False
            for selector in selectors:
                for a in soup.select(selector)[:10]:  # Limitar a 10 por seletor
                    text = a.text.strip() if a.text else None
                    href = a.get('href', '')
                    
                    # Filtrar apenas links relevantes
                    if text and len(text) > 5 and href and any(x in href for x in ['jusbrasil.com.br', '/busca/', '/processos/', '/jurisprudencia/']):
                        url_full = href if href.startswith('http') else f'https://www.jusbrasil.com.br{href}'
                        
                        result = {
                            'title': text[:100],
                            'url': url_full,
                            'source': 'jusbrasil',
                            'tipo': 'jurisprudencia' if '/jurisprudencia/' in href else 'processo'
                        }
                        
                        # Evitar duplicatas
                        if not any(r['url'] == result['url'] for r in res):
                            res.append(result)
                            found_results = True
                
                if found_results and len(res) >= 3:
                    break
            
            if res:
                print(f"[JusbrasilScraper] Found {len(res)} results")
            else:
                print(f"[JusbrasilScraper] No results found")
            
            return res[:20]  # Limitar a 20 resultados
            
        except Exception as e:
            print(f"[JusbrasilScraper] Error: {e}")
            return []
