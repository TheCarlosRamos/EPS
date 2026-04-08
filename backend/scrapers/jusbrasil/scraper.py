import requests
from bs4 import BeautifulSoup
from scrapers.base import BaseScraper

class JusbrasilScraper(BaseScraper):
    name = 'jusbrasil'
    supported_types = ["NAME", "CPF"]
    
    def search(self, intent):
        q = intent['value']
        url = f'https://www.jusbrasil.com.br/busca?q={q}'
        headers = {"User-Agent": "Mozilla/5.0"}
        
        try:
            r = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(r.text, 'html.parser')
            res = []
            for a in soup.select('a.resultado-busca-link'):
                res.append({'title': a.text.strip(), 'url': a['href']})
            return res
        except Exception:
            return []
