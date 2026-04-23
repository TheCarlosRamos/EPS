import requests
import random
import os
from scrapers.base import BaseScraper

class InstagramScraper(BaseScraper):
    name = "instagram"
    supported_types = ["NAME", "EMAIL"]
    
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ]

    def search(self, intent):
        q = intent['value'].replace(' ', '').lower()
        
        # Se for e-mail, extrair apenas a parte antes do @
        if intent.get('type') == 'EMAIL':
            if '@' in q:
                q = q.split('@')[0]
            else:
                return []
        
        # Validar username: apenas letras, números, pontos e underscores
        if not q or not all(c.isalnum() or c in '._' for c in q):
            return []
        
        url = f"https://www.instagram.com/{q}/"
        
        # Suporte a proxy para anonimato (RNF01)
        proxy = os.getenv('HTTP_PROXY')
        proxies = {'http': proxy, 'https': proxy} if proxy else None
        
        try:
            headers = {
                "User-Agent": random.choice(self.USER_AGENTS),
                "Accept-Language": "pt-BR,pt;q=0.9"
            }
            r = requests.get(url, headers=headers, timeout=10, proxies=proxies, allow_redirects=False)
            
            if r.status_code in [200, 302]:
                return [{
                    "profile": q,
                    "url": url,
                    "source": "instagram",
                    "exists": r.status_code == 200
                }]
        except Exception as e:
            print(f"Instagram scraper error: {e}")
        
        return []
