import requests
from bs4 import BeautifulSoup
from scrapers.base import BaseScraper

class JusbrasilScraper(BaseScraper):
    name='jusbrasil'
    def search(self,intent):
        q=intent['value']
        url=f'https://www.jusbrasil.com.br/busca?q={q}'
        r=requests.get(url,timeout=10)
        soup=BeautifulSoup(r.text,'html.parser')
        res=[]
        for a in soup.select('a.resultado-busca-link'):
            res.append({'title':a.text.strip(),'url':a['href']})
        return res
