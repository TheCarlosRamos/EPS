import requests
import random
from bs4 import BeautifulSoup
from scrapers.base import BaseScraper

class GoogleScraper(BaseScraper):
    name = "google"
    supported_types = ["NAME", "CPF", "EMAIL", "PHONE"]
    
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ]

    def search(self, intent):
        q = intent['value']
        url = f"https://www.google.com/search?q={q}"
        headers = {"User-Agent": random.choice(self.USER_AGENTS)}
        
        try:
            r = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(r.text, 'html.parser')
            results = []
            for g in soup.select('div.g'):
                title = g.select_one('h3')
                link = g.select_one('a')
                if title and link:
                    results.append({"title": title.text, "url": link['href']})
            return results
        except Exception:
            return []
