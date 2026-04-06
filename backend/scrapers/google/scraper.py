import requests
from bs4 import BeautifulSoup
from scrapers.base import BaseScraper

class GoogleScraper(BaseScraper):
    name = "google"
    def search(self, intent):
        q = intent['value']
        url = f"https://www.google.com/search?q={q}"
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        results = []
        for g in soup.select('div.g'):
            title = g.select_one('h3')
            link = g.select_one('a')
            if title and link:
                results.append({"title": title.text, "url": link['href']})
        return results
