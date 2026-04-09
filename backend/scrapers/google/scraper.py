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
        url = f"https://www.google.com/search?q={q}&hl=pt-BR"
        
        # Suporte a proxy para anonimato (RNF01)
        proxy = os.getenv('HTTP_PROXY')
        proxies = {'http': proxy, 'https': proxy} if proxy else None
        
        for attempt in range(3):  # Retry até 3 vezes
            try:
                headers = {
                    "User-Agent": random.choice(self.USER_AGENTS),
                    "Accept-Language": "pt-BR,pt;q=0.9"
                }
                r = requests.get(url, headers=headers, timeout=10, proxies=proxies)
                
                if r.status_code == 403:
                    print(f"Google returned 403 (blocked), attempt {attempt+1}/3")
                    time.sleep(2 ** attempt)
                    continue
                    
                soup = BeautifulSoup(r.text, 'html.parser')
                results = []
                
                for g in soup.select('div.g, div[data-sokoban-container]'):
                    title = g.select_one('h3')
                    link = g.select_one('a[href^="/url"]')
                    
                    if title and link and 'href' in link.attrs:
                        url_clean = link['href'].split('&')[0].replace('/url?q=', '')
                        if url_clean.startswith('http'):
                            results.append({
                                "title": title.text.strip(),
                                "url": url_clean,
                                "source": "google"
                            })
                
                return results if results else []
            except requests.exceptions.RequestException as e:
                print(f"Google scraper request error (attempt {attempt+1}/3): {e}")
                time.sleep(2 ** attempt)
        
        print("Google scraper: All retries exhausted")
        return []
