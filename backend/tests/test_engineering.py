"""
Testes de engenharia real para OSINT
Contratos, falhas, concorrência e resiliência
"""

import pytest
import time
import threading
from unittest.mock import patch, MagicMock, Mock
from fastapi.testclient import TestClient

from main import app
from core.cache import cache
from core.circuit_breaker import CircuitBreaker, CircuitConfig, CircuitState
from core.scraper_base import ScraperResult, BaseScraper
from workers.tasks import run_search

client = TestClient(app)

# -----------------------------
# CONTRATOS (Contract Tests)
# -----------------------------

def test_scraper_result_contract():
    """Todo scraper result DEVE seguir contrato"""
    result = ScraperResult('test', {
        'source': 'test',
        'type': 'profile',
        'value': 'test_value',
        'url': 'http://test.com'
    })
    
    dict_result = result.to_dict()
    
    # Campos obrigatórios
    required_fields = ScraperResult.REQUIRED_FIELDS
    for field in required_fields:
        assert field in dict_result, f"Missing required field: {field}"
    
    # Campos automáticos
    assert 'hash' in dict_result
    assert 'timestamp' in dict_result
    assert dict_result['source'] == 'test'

def test_cache_contract():
    """Cache DEVE seguir contrato de chave normalizada"""
    intent1 = {'type': 'EMAIL', 'value': 'Test@Example.COM'}
    intent2 = {'type': 'EMAIL', 'value': 'test@example.com'}
    
    # Devem gerar mesma chave
    key1 = cache._generate_cache_key(intent1)
    key2 = cache._generate_cache_key(intent2)
    
    assert key1 == key2, "Cache keys should be normalized"

# -----------------------------
# TESTES DE FALHA (os mais importantes)
# -----------------------------

@patch('requests.get')
def test_scraper_timeout(mock_get):
    """Scraper DEVE handle timeout gracefully"""
    from requests.exceptions import Timeout
    mock_get.side_effect = Timeout("Request timeout")
    
    from scrapers.google.scraper import GoogleScraper
    scraper = GoogleScraper()
    results = scraper.search({'type': 'NAME', 'value': 'test'})
    
    # DEVE retornar lista vazia, não exceção
    assert isinstance(results, list)
    assert len(results) == 0

@patch('requests.get')
def test_scraper_403_forbidden(mock_get):
    """Scraper DEVE handle HTTP 403"""
    mock_resp = Mock()
    mock_resp.status_code = 403
    mock_get.return_value = mock_resp
    
    from scrapers.instagram.scraper import InstagramScraper
    scraper = InstagramScraper()
    results = scraper.search({'type': 'NAME', 'value': 'test'})
    
    assert isinstance(results, list)
    # Pode retornar vazio ou resultados parciais

@patch('requests.get')
def test_scraper_malformed_html(mock_get):
    """Scraper DEVE handle HTML quebrado"""
    mock_resp = Mock()
    mock_resp.text = '<html><body><h3>Broken</h3><a href="'
    mock_get.return_value = mock_resp
    
    from scrapers.google.scraper import GoogleScraper
    scraper = GoogleScraper()
    results = scraper.search({'type': 'NAME', 'value': 'test'})
    
    # Não deve quebrar
    assert isinstance(results, list)

def test_scraper_empty_response():
    """Scraper DEVE handle resposta vazia"""
    from scrapers.google.scraper import GoogleScraper
    scraper = GoogleScraper()
    results = scraper.search({'type': 'NAME', 'value': ''})
    
    assert isinstance(results, list)

# -----------------------------
# CIRCUIT BREAKER TESTES
# -----------------------------

def test_circuit_breaker_opens_on_failures():
    """Circuit DEVE abrir após falhas"""
    config = CircuitConfig(failure_threshold=3, recovery_timeout=1)
    breaker = CircuitBreaker('test', config)
    
    # Simula falhas
    def failing_func():
        raise Exception("Simulated failure")
    
    # 3 falhas devem abrir circuit
    for i in range(3):
        breaker.call(failing_func)
    
    assert breaker.state == CircuitState.OPEN

def test_circuit_breaker_recovers():
    """Circuit DEVE recuperar após timeout"""
    config = CircuitConfig(failure_threshold=2, recovery_timeout=1)
    breaker = CircuitBreaker('test', config)
    
    # Força abertura
    def failing_func():
        raise Exception("Failure")
    
    breaker.call(failing_func)
    breaker.call(failing_func)
    
    assert breaker.state == CircuitState.OPEN
    
    # Espera timeout
    time.sleep(1.1)
    
    # Próxima chamada deve tentar recuperação
    def success_func():
        return ["success"]
    
    result = breaker.call(success_func)
    assert result == ["success"]

# -----------------------------
# TESTES DE CONCORRÊNCIA
# -----------------------------

def test_concurrent_searches_use_cache():
    """Buscas concorrentes DEVE usar cache apenas uma vez"""
    with patch('core.cache.cache.get') as mock_get, \
         patch('core.cache.cache.set') as mock_set, \
         patch('workers.tasks.run_search.delay') as mock_task:
        
        # Mock da task para simular resposta rápida
        mock_task.return_value = MagicMock(id='test-task-id')
        
        # Primeira chamada sem cache
        mock_get.return_value = None
        
        def run_search_thread():
            return client.post('/search', json={'query': 'test@example.com'}, 
                           headers={'Authorization': 'Bearer fake-token'})
        
        # Executa múltiplas buscas simultâneas
        threads = []
        for i in range(5):
            thread = threading.Thread(target=run_search_thread)
            threads.append(thread)
            thread.start()
        
        # Espera todas terminarem
        for thread in threads:
            thread.join()
        
        # Cache DEVE ser chamado 5 vezes (buscas)
        # Mas set DEVE ser chamado apenas 1 vez (primeira)
        print(f"Cache get calls: {mock_get.call_count}")
        print(f"Cache set calls: {mock_set.call_count}")
        assert mock_get.call_count == 5
        assert mock_set.call_count == 1

def test_cache_invalidation():
    """Cache DEVE invalidar por padrão"""
    # Simula dados em cache
    intent = {'type': 'EMAIL', 'value': 'test@example.com'}
    cache.set(intent, {'results': ['cached']}, ttl_minutes=1)
    
    # Verifica que existe
    cached = cache.get(intent)
    assert cached is not None
    
    # Invalida
    cache.invalidate_pattern('osint:*')
    
    # Verifica que foi removido
    cached_after = cache.get(intent)
    assert cached_after is None

# -----------------------------
# TESTES DE PERFORMANCE
# -----------------------------

def test_search_performance_under_limit():
    """Busca DEVE completar em tempo razoável"""
    start_time = time.time()
    
    # Usa cache para teste rápido
    intent = {'type': 'EMAIL', 'value': 'test@example.com'}
    cache.set(intent, {'results': []}, ttl_minutes=1)
    
    # Simula task (sem Celery real)
    from workers.tasks import _format_results
    result = _format_results({'results': []})
    
    execution_time = time.time() - start_time
    
    # DEVE ser rápido (com cache)
    assert execution_time < 1.0
    assert 'metadata' in result
    assert result['metadata']['cache_hit'] is True

# -----------------------------
# TESTES DE SEGURANÇA
# -----------------------------

def test_jwt_secret_not_hardcoded():
    """JWT secret DEVE vir de environment"""
    # Este teste verifica se existe variável de ambiente
    import os
    secret = os.getenv('JWT_SECRET', 'pcdf-secret')
    
    # Em produção, não deveria ser o padrão
    assert secret != 'pcdf-secret' or 'development' in os.getenv('ENV', '')

def test_audit_log_structure():
    """Log de auditoria DEVE ter estrutura padrão"""
    from audit.logger import log
    
    # Captura log (mock)
    with patch('builtins.print') as mock_print:
        log({'action': 'test', 'user': 'test_user'})
        
        # Verifica se foi chamado
        mock_print.assert_called_once()
        
        # Verifica estrutura (depende da implementação)
        call_args = mock_print.call_args[0][0]
        assert 'action' in call_args
        assert 'timestamp' in call_args

# -----------------------------
# INTEGRAÇÃO COM CIRCUIT BREAKER
# -----------------------------

@patch('core.cache.cache.get')
def test_search_with_circuit_breaker(mock_cache):
    """Busca DEVE respeitar circuit breaker"""
    # Cache miss
    mock_cache.return_value = None
    
    # Simula circuit breaker aberto
    with patch('core.circuit_breaker.get_circuit_breaker') as mock_cb:
        mock_breaker = MagicMock()
        mock_breaker.call.return_value = []  # Circuit breaker aberto
        mock_cb.return_value = mock_breaker
        
        # Executa busca
        result = run_search('test@example.com')
        
        # DEVE ter resultados vazios do scraper protegido
        assert 'results' in result
        assert isinstance(result['results'], list)

# -----------------------------
# FIXTURES
# -----------------------------

@pytest.fixture
def mock_auth_header():
    """Fixture para autenticação mockada"""
    return {'Authorization': 'Bearer fake-test-token'}

@pytest.fixture
def sample_intent():
    """Fixture para intenção de teste"""
    return {'type': 'EMAIL', 'value': 'test@example.com'}

@pytest.fixture
def circuit_breaker_config():
    """Fixture para config de circuit breaker"""
    return CircuitConfig(
        failure_threshold=2,
        recovery_timeout=1,
        success_threshold=1
    )
