import requests
import random
import time
import os
from bs4 import BeautifulSoup
from scrapers.base import BaseScraper

class GoogleScraper(BaseScraper):
    name = "google"
    supported_types = ["NAME", "CPF", "EMAIL", "PHONE"]
    
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15"
    ]

    def search(self, intent):
        q = intent['value']
        url = f"https://www.google.com/search?q={q}&hl=pt-BR&num=10"
        
        # Suporte a proxy para anonimato (RNF01)
        proxy = os.getenv('HTTP_PROXY')
        proxies = {'http': proxy, 'https': proxy} if proxy else None
        
        for attempt in range(3):  # Retry até 3 vezes
            try:
                headers = {
                    "User-Agent": random.choice(self.USER_AGENTS),
                    "Accept-Language": "pt-BR,pt;q=0.9",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
                }
                r = requests.get(url, headers=headers, timeout=10, proxies=proxies)
                print(f"[GoogleScraper] Status: {r.status_code}, Content length: {len(r.text)}")
                
                if r.status_code == 403:
                    print(f"[GoogleScraper] 403 Forbidden (blocked), attempt {attempt+1}/3")
                    time.sleep(2 ** attempt)
                    continue
                
                if r.status_code != 200:
                    print(f"[GoogleScraper] Unexpected status {r.status_code}, retrying...")
                    time.sleep(2 ** attempt)
                    continue
                    
                soup = BeautifulSoup(r.text, 'html.parser')
                results = []
                
                # Tentar múltiplos seletores diferentes
                selectors = [
                    'div.g',  # Seletor padrão do Google
                    'div[data-sokoban-container]',  # Novo layout
                    'div.Gd8Csd',  # Container de resultado
                    'a[href^="http"][data-rw]',  # Links com data-rw
                ]
                
                found_links = False
                for selector in selectors:
                    for item in soup.select(selector)[:5]:  # Limitar a 5 por seletor
                        # Tentar encontrar título
                        title_elem = item.select_one('h3, [role="heading"]')
                        
                        # Tentar encontrar link
                        link_elem = None
                        for link in item.select('a'):
                            if link.get('href', '').startswith(('http', '/url')):
                                link_elem = link
                                break
                        
                        if title_elem and link_elem and 'href' in link_elem.attrs:
                            href = link_elem['href']
                            # Limpar URL do Google
                            if '/url?q=' in href:
                                url_clean = href.split('&')[0].replace('/url?q=', '')
                            else:
                                url_clean = href
                            
                            if url_clean.startswith(('http://', 'https://')):
                                result = {
                                    "title": title_elem.text.strip()[:100],
                                    "url": url_clean,
                                    "source": "google"
                                }
                                # Evitar duplicatas
                                if not any(r['url'] == result['url'] for r in results):
                                    results.append(result)
                                    found_links = True
                    
                    if found_links and len(results) >= 3:
                        break
                
                if results:
                    print(f"[GoogleScraper] Found {len(results)} results")
                    return results
                else:
                    print(f"[GoogleScraper] No results found with any selector, attempt {attempt+1}/3")
                    
            except requests.exceptions.Timeout:
                print(f"[GoogleScraper] Timeout (attempt {attempt+1}/3)")
                time.sleep(2 ** attempt)
            except Exception as e:
                print(f"[GoogleScraper] Error (attempt {attempt+1}/3): {e}")
                time.sleep(2 ** attempt)
        
        print("[GoogleScraper] All retries exhausted")
        return []
