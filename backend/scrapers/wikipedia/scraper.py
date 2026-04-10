import requests
from bs4 import BeautifulSoup
from scrapers.base import BaseScraper
import re

class WikipediaScraper(BaseScraper):
    """Scraper para Wikipedia usando API MediaWiki"""
    name = 'wikipedia'
    supported_types = ["NAME", "ORGANIZATION", "PERSON"]
    
    BASE_URL = "https://pt.wikipedia.org/w/api.php"
    WIKI_URL = "https://pt.wikipedia.org/wiki"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def search(self, intent):
        """Busca na Wikipedia usando API MediaWiki"""
        q = intent['value']
        try:
            # Busca via API
            results = self._search_api(q)
            
            if results:
                return results[:10]
            
            # Fallback: tentar acesso direto
            return self._search_direct(q)
            
        except Exception as e:
            print(f'[WikipediaScraper] Error: {e}')
            return []
    
    def _search_api(self, q):
        """Busca via API MediaWiki (recomendado)"""
        try:
            params = {
                'action': 'query',
                'list': 'search',
                'srsearch': q,
                'srlimit': 10,
                'srinfo': 'totalhits',
                'format': 'json'
            }
            
            r = self.session.get(self.BASE_URL, params=params, timeout=10)
            r.raise_for_status()
            data = r.json()
            
            results = []
            search_results = data.get('query', {}).get('search', [])
            total_hits = data.get('query', {}).get('searchinfo', {}).get('totalhits', 0)
            
            for item in search_results:
                title = item.get('title', '')
                pageid = item.get('pageid', '')
                snippet = item.get('snippet', '')
                timestamp = item.get('timestamp', '')
                
                # Limpar snippet do HTML
                snippet_clean = re.sub('<[^<]+?>', '', snippet)
                
                results.append({
                    'title': title,
                    'url': f'{self.WIKI_URL}/{title.replace(" ", "_")}',
                    'snippet': snippet_clean,
                    'pageid': pageid,
                    'source': 'wikipedia',
                    'tipo': 'enciclopedia',
                    'data': timestamp,
                    'total_hits': total_hits
                })
            
            print(f'[WikipediaScraper] Encontrados {len(results)}/{total_hits} resultados')
            return results
            
        except Exception as e:
            print(f'[WikipediaScraper-API] Error: {e}')
            return []
    
    def _search_direct(self, q):
        """Fallback: busca direta na página de busca HTML"""
        try:
            url = f'{self.WIKI_URL}/Especial:Busca'
            params = {'search': q, 'go': 'Ir'}
            
            r = self.session.get(url, params=params, timeout=10)
            soup = BeautifulSoup(r.text, 'html.parser')
            
            results = []
            
            # Procurar resultados de busca
            for li in soup.select('li.mw-search-result'):
                title_elem = li.select_one('a.mw-search-result-title')
                snippet_elem = li.select_one('div.mw-search-result-data')
                
                if title_elem:
                    title = title_elem.text.strip()
                    href = title_elem.get('href', '')
                    snippet = snippet_elem.text.strip() if snippet_elem else ''
                    
                    results.append({
                        'title': title,
                        'url': f'https://pt.wikipedia.org{href}' if href.startswith('/') else href,
                        'snippet': snippet,
                        'source': 'wikipedia',
                        'tipo': 'enciclopedia'
                    })
            
            return results[:10]
            
        except Exception as e:
            print(f'[WikipediaScraper-Direct] Error: {e}')
            return []
