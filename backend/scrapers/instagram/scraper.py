import requests
import random
from scrapers.base import BaseScraper

class InstagramScraper(BaseScraper):
    name = "instagram"
    supported_types = ["NAME", "EMAIL"]
    
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ]

    def search(self, intent):
        q = intent['value'].replace(' ', '')
        url = f"https://www.instagram.com/{q}/"
        headers = {"User-Agent": random.choice(self.USER_AGENTS)}
        
        try:
            r = requests.get(url, headers=headers, timeout=10)
            if r.status_code == 200:
                return [{"profile": q, "url": url}]
        except Exception:
            pass
        return []
