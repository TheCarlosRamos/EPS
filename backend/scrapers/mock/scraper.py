"""
Scraper de Fallback para Testes
Quando Google e Jusbrasil não conseguem dados reais, retorna dados simulados
para fins de demonstração
"""
import random
from scrapers.base import BaseScraper

class MockScraper(BaseScraper):
    name = "mock"
    supported_types = ["NAME", "CPF", "EMAIL", "PHONE"]
    
    MOCK_DATA = {
        "nome": [
            {"title": "[Teste] Processo Judicial - Pessoa", "url": "https://www.jusbrasil.com.br/processos/teste1", "source": "mock"},
            {"title": "[Teste] Jurisprudência relacionada", "url": "https://www.jusbrasil.com.br/jurisprudencia/teste1", "source": "mock"},
            {"title": "[Teste] Perfil em site de busca", "url": "https://www.exemplo.com.br/pessoas/teste1", "source": "mock"},
        ],
        "cpf": [
            {"title": "[Teste] Resultado de processo CPF", "url": "https://www.jusbrasil.com.br/busca?q=cpf123", "source": "mock"},
            {"title": "[Teste] Informação financeira", "url": "https://www.serasa.com.br/teste", "source": "mock"},
        ],
        "email": [
            {"title": "[Teste] Resultado de busca por e-mail", "url": "https://www.google.com/search?q=email", "source": "mock"},
        ]
    }
    
    def search(self, intent):
        # Retornar dados mock apenas se KEY for "DEMO" (para testes)
        tipo = intent.get('type', 'nome').lower()
        chave = intent.get('value', '').lower()
        
        # Ativar mock apenas com prefixo DEMO
        if chave.startswith('demo'):
            results = self.MOCK_DATA.get(tipo, self.MOCK_DATA["nome"])
            return results[:3]
        
        return []
