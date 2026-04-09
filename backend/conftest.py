"""
Configuração profissional de testes para OSINT
Fixtures, mocks e configurações globais
"""

import pytest
import os
import sys
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

# Adiciona path do backend
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

# Variáveis de ambiente para testes
os.environ['ENV'] = 'testing'
os.environ['JWT_SECRET'] = 'test-secret-key-32-chars-long'

@pytest.fixture(scope='session')
def test_client():
    """Client de teste para toda sessão"""
    from main import app
    return TestClient(app)

@pytest.fixture
def auth_header(test_client):
    """Header de autenticação para testes"""
    response = test_client.post('/login')
    assert response.status_code == 200
    token = response.json()['access_token']
    return {'Authorization': f'Bearer {token}'}

@pytest.fixture
def mock_redis():
    """Mock de Redis para testes"""
    with patch('core.cache.redis.Redis') as mock_redis:
        mock_instance = MagicMock()
        mock_redis.return_value = mock_instance
        
        # Configura comportamentos básicos
        mock_instance.ping.return_value = True
        mock_instance.get.return_value = None
        mock_instance.setex.return_value = True
        mock_instance.keys.return_value = []
        mock_instance.delete.return_value = True
        mock_instance.info.return_value = {
            'used_memory_human': '1M',
            'connected_clients': 1,
            'total_commands_processed': 100
        }
        
        yield mock_instance

@pytest.fixture
def sample_scrapers():
    """Scrapers de exemplo para testes"""
    class MockScraper:
        def __init__(self, name):
            self.name = name
            self.supported_types = ['EMAIL', 'NAME']
        
        def search(self, intent):
            return [{'source': self.name, 'value': intent['value']}]
        
        def get_status(self):
            return {'name': self.name, 'session_active': False}
    
    return [
        MockScraper('google'),
        MockScraper('instagram'),
        MockScraper('jusbrasil')
    ]

@pytest.fixture
def sample_intent():
    """Intenção de exemplo para testes"""
    return {
        'type': 'EMAIL',
        'value': 'test@example.com',
        'original': 'test@example.com'
    }

@pytest.fixture
def circuit_breaker_config():
    """Configuração de circuit breaker para testes"""
    from core.circuit_breaker import CircuitConfig
    return CircuitConfig(
        failure_threshold=2,
        recovery_timeout=1,
        success_threshold=1,
        timeout=5
    )

# Marks para categorização de testes
pytest_marks = {
    'unit': pytest.mark.unit,           # Testes unitários rápidos
    'integration': pytest.mark.integration, # Testes de integração
    'slow': pytest.mark.slow,           # Testes lentos (network)
    'external': pytest.mark.external,     # Testes que dependem de serviços externos
    'contract': pytest.mark.contract,     # Testes de contrato
    'resilience': pytest.mark.resilience, # Testes de resiliência
}

def pytest_configure(config):
    """Configura marks customizados"""
    for mark_name, mark in pytest_marks.items():
        config.addinivalue_line('markers', mark)

def pytest_collection_modifyitems(config, items):
    """Adiciona marks automaticamente"""
    for item in items:
        # Testes unitários por padrão
        if 'test_' in item.name and not any(mark in item.keywords for mark in ['integration', 'slow', 'external']):
            item.add_marker(pytest_marks['unit'])
        
        # Testes de integração
        if 'integration' in item.nodeid:
            item.add_marker(pytest_marks['integration'])
        
        # Testes lentos
        if any(keyword in item.name.lower() for keyword in ['timeout', 'sleep', 'wait']):
            item.add_marker(pytest_marks['slow'])
