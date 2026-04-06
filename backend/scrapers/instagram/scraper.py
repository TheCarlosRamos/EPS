import requests
from scrapers.base import BaseScraper

class InstagramScraper(BaseScraper):
    name = "instagram"
    def search(self, intent):
        q = intent['value'].replace(' ', '')
        url = f"https://www.instagram.com/{q}/"
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return [{"profile": q, "url": url}]
        return []
