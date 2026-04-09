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
                "Accept-Language": "pt-BR,pt;q=0.9"
            }
            r = requests.get(url, headers=headers, timeout=10, proxies=proxies)
            
            soup = BeautifulSoup(r.text, 'html.parser')
            res = []
            
            # Tentar múltiplos seletores
            for a in soup.select('a.resultado-busca-link, a[href*="/busca/"], .resultado-busca link'):
                if a.text.strip() and 'href' in a.attrs:
                    href = a['href']
                    if any(x in href for x in ['jusbrasil.com.br', '/processos/', '/jurisprudencia/']):
                        res.append({
                            'title': a.text.strip(),
                            'url': href if href.startswith('http') else f'https://www.jusbrasil.com.br{href}',
                            'source': 'jusbrasil',
                            'tipo': 'jurisprudencia' if '/jurisprudencia/' in href else 'processo'
                        })
            
            return res[:20]
        except Exception as e:
            print(f"Jusbrasil scraper error: {e}")
            return []
