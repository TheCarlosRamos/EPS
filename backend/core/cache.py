"""
Cache Redis estratégico para OSINT
Camada inteligente de cache com TTL diferenciado por fonte
"""

import redis
import json
import hashlib
from typing import Optional, Dict, Any
from datetime import timedelta

class OSINTCache:
    def __init__(self, host='redis', port=6379, db=0):
        self.redis = redis.Redis(host=host, port=port, db=0, decode_responses=True)
        self._test_connection()
    
    def _test_connection(self):
        """Testa conexão com Redis"""
        try:
            self.redis.ping()
            return True
        except Exception as e:
            print(f"Redis connection failed: {e}")
            return False
    
    def _normalize_query(self, query: str) -> str:
        """Normaliza query para cache key"""
        return query.lower().strip()
    
    def _generate_cache_key(self, intent: Dict[str, Any]) -> str:
        """Gera chave de cache baseada na intenção"""
        normalized = self._normalize_query(intent.get('value', ''))
        intent_type = intent.get('type', 'unknown')
        
        # Hash para evitar chaves muito longas
        query_hash = hashlib.md5(normalized.encode()).hexdigest()[:8]
        return f"osint:{intent_type}:{query_hash}"
    
    def get(self, intent: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Busca resultados em cache"""
        if not self._test_connection():
            return None
        
        cache_key = self._generate_cache_key(intent)
        try:
            cached = self.redis.get(cache_key)
            if cached:
                print(f"Cache HIT for {cache_key}")
                return json.loads(cached)
            print(f"Cache MISS for {cache_key}")
            return None
        except Exception as e:
            print(f"Cache get error: {e}")
            return None
    
    def set(self, intent: Dict[str, Any], results: Dict[str, Any], ttl_minutes: int = 30):
        """Armazena resultados em cache com TTL"""
        if not self._test_connection():
            return False
        
        cache_key = self._generate_cache_key(intent)
        try:
            # TTL diferente por fonte
            if 'google' in str(results):
                ttl = timedelta(minutes=15)  # Google muda rápido
            elif 'instagram' in str(results):
                ttl = timedelta(hours=1)   # Instagram mais estável
            else:
                ttl = timedelta(minutes=ttl_minutes)
            
            success = self.redis.setex(
                cache_key, 
                int(ttl.total_seconds()), 
                json.dumps(results)
            )
            print(f"Cache SET for {cache_key} (TTL: {ttl})")
            return success
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    def invalidate_pattern(self, pattern: str):
        """Invalida cache por padrão"""
        if not self._test_connection():
            return False
        
        try:
            keys = self.redis.keys(pattern)
            if keys:
                self.redis.delete(*keys)
                print(f"Invalidated {len(keys)} cache entries for pattern: {pattern}")
            return True
        except Exception as e:
            print(f"Cache invalidate error: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Estatísticas do cache"""
        if not self._test_connection():
            return {}
        
        try:
            info = self.redis.info()
            return {
                'used_memory': info.get('used_memory_human', 'N/A'),
                'connected_clients': info.get('connected_clients', 0),
                'total_commands': info.get('total_commands_processed', 0)
            }
        except Exception as e:
            print(f"Cache stats error: {e}")
            return {}

# Instância global para uso em toda aplicação
cache = OSINTCache()
