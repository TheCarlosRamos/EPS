"""
Circuit Breaker para resiliência de scrapers
Impede cascata de falhas e recuperação automática
"""

import time
from typing import Dict, Callable, Any
from enum import Enum
from dataclasses import dataclass

class CircuitState(Enum):
    CLOSED = "closed"      # Funcionando normal
    OPEN = "open"         # Desligado por falhas
    HALF_OPEN = "half_open" # Testando recuperação

@dataclass
class CircuitConfig:
    failure_threshold: int = 5      # Falhas para abrir
    recovery_timeout: int = 60       # Segundos para tentar recuperação
    success_threshold: int = 2       # Sucessos para fechar (half_open)
    timeout: int = 30               # Timeout por tentativa

class CircuitBreaker:
    def __init__(self, name: str, config: CircuitConfig = None):
        self.name = name
        self.config = config or CircuitConfig()
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = 0
        self.state_history = []
    
    def __call__(self, func: Callable) -> Callable:
        """Decorator para aplicação do circuit breaker"""
        def wrapper(*args, **kwargs):
            return self.call(func, *args, **kwargs)
        return wrapper
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Executa função com proteção do circuit breaker"""
        # Verifica estado atual
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                self.success_count = 0
                print(f"Circuit {self.name}: HALF_OPEN - testing recovery")
            else:
                print(f"Circuit {self.name}: OPEN - skipping execution")
                return []
        
        # Executa função protegida
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            print(f"Circuit {self.name}: FAILURE - {str(e)}")
            return []
    
    def _should_attempt_reset(self) -> bool:
        """Verifica se deve tentar resetar"""
        return time.time() - self.last_failure_time >= self.config.recovery_timeout
    
    def _on_success(self):
        """Ação em caso de sucesso"""
        self.failure_count = 0
        
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.config.success_threshold:
                self.state = CircuitState.CLOSED
                print(f"Circuit {self.name}: CLOSED - recovered!")
        elif self.state == CircuitState.CLOSED:
            print(f"Circuit {self.name}: SUCCESS - staying closed")
        
        self._record_state("SUCCESS")
    
    def _on_failure(self):
        """Ação em caso de falha"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.state == CircuitState.CLOSED:
            if self.failure_count >= self.config.failure_threshold:
                self.state = CircuitState.OPEN
                print(f"Circuit {self.name}: OPEN - too many failures!")
        elif self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.OPEN
            print(f"Circuit {self.name}: OPEN - recovery failed!")
        
        self._record_state("FAILURE")
    
    def _record_state(self, event: str):
        """Registra mudança de estado"""
        self.state_history.append({
            'timestamp': time.time(),
            'state': self.state.value,
            'event': event
        })
        
        # Mantém apenas histórico recente
        if len(self.state_history) > 100:
            self.state_history = self.state_history[-50:]
    
    def get_status(self) -> Dict[str, Any]:
        """Status atual do circuit breaker"""
        return {
            'name': self.name,
            'state': self.state.value,
            'failure_count': self.failure_count,
            'success_count': self.success_count,
            'last_failure': self.last_failure_time,
            'config': {
                'failure_threshold': self.config.failure_threshold,
                'recovery_timeout': self.config.recovery_timeout,
                'success_threshold': self.config.success_threshold
            }
        }
    
    def reset(self):
        """Reseta manualmente o circuit breaker"""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = 0
        print(f"Circuit {self.name}: MANUAL RESET")

# Registry global de circuit breakers
_circuit_breakers: Dict[str, CircuitBreaker] = {}

def get_circuit_breaker(name: str, config: CircuitConfig = None) -> CircuitBreaker:
    """Obtém ou cria circuit breaker"""
    if name not in _circuit_breakers:
        _circuit_breakers[name] = CircuitBreaker(name, config)
    return _circuit_breakers[name]

def circuit_breaker(name: str, config: CircuitConfig = None):
    """Decorator para aplicar circuit breaker"""
    def decorator(func: Callable) -> Callable:
        breaker = get_circuit_breaker(name, config)
        return breaker(func)
    return decorator

def get_all_circuit_breakers_status() -> Dict[str, Dict[str, Any]]:
    """Status de todos os circuit breakers"""
    return {name: cb.get_status() for name, cb in _circuit_breakers.items()}
