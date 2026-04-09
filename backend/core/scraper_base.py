"""
Base para scrapers idempotentes e determinísticos
Separa: extração → normalização → deduplicação
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
import hashlib
import re

class ScraperResult:
    """Resultado padronizado de scraper"""
    
    REQUIRED_FIELDS = ['source', 'type', 'value', 'url']
    
    def __init__(self, source: str, data: Dict[str, Any]):
        self.source = source
        self.data = data
        self.timestamp = datetime.now().isoformat()
        self.hash = self._generate_hash()
    
    def _generate_hash(self) -> str:
        """Gera hash único para deduplicação"""
        content = f"{self.source}{str(self.data)}{self.timestamp}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário padronizado"""
        result = {
            'source': self.source,
            'hash': self.hash,
            'timestamp': self.timestamp,
            **self.data
        }
        
        # Valida campos obrigatórios
        missing = [f for f in self.REQUIRED_FIELDS if f not in result]
        if missing:
            raise ValueError(f"Missing required fields: {missing}")
        
        return result
    
    def is_valid(self) -> bool:
        """Valida estrutura do resultado"""
        try:
            self.to_dict()
            return True
        except ValueError:
            return False

class BaseScraper(ABC):
    """Classe base para scrapers idempotentes"""
    
    def __init__(self, name: str):
        self.name = name
        self.session = None  # Sessão HTTP reutilizável
    
    @abstractmethod
    def _extract_raw(self, intent: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extrai dados brutos da fonte (idempotente)"""
        pass
    
    def _normalize(self, raw_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Normaliza resultados para formato padrão"""
        normalized = []
        for item in raw_results:
            try:
                # Limpeza básica
                if 'title' in item:
                    item['title'] = self._clean_text(item['title'])
                if 'description' in item:
                    item['description'] = self._clean_text(item['description'])
                
                # Garante campos obrigatórios
                item.setdefault('source', self.name)
                item.setdefault('type', 'unknown')
                item.setdefault('value', '')
                
                normalized.append(item)
            except Exception as e:
                print(f"Normalization error in {self.name}: {e}")
                continue
        
        return normalized
    
    def _deduplicate(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicatas baseado em hash"""
        seen_hashes = set()
        deduplicated = []
        
        for item in results:
            # Gera hash simples para deduplicação
            content = f"{item.get('url', '')}{item.get('title', '')}{item.get('value', '')}"
            item_hash = hashlib.md5(content.encode()).hexdigest()
            
            if item_hash not in seen_hashes:
                seen_hashes.add(item_hash)
                deduplicated.append(item)
        
        return deduplicated
    
    def _clean_text(self, text: str) -> str:
        """Limpeza de texto"""
        if not text:
            return ""
        
        # Remove espaços extras
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove caracteres especiais perigosos
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
        
        return text
    
    def search(self, intent: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Método principal de busca (determinístico)"""
        try:
            print(f"[{self.name}] Starting search for: {intent}")
            
            # 1. Extração bruta
            raw_results = self._extract_raw(intent)
            print(f"[{self.name}] Extracted {len(raw_results)} raw results")
            
            # 2. Normalização
            normalized = self._normalize(raw_results)
            print(f"[{self.name}] Normalized to {len(normalized)} results")
            
            # 3. Deduplicação
            deduplicated = self._deduplicate(normalized)
            print(f"[{self.name}] Deduplicated to {len(deduplicated)} results")
            
            # 4. Validação final
            valid_results = []
            for item in deduplicated:
                try:
                    result = ScraperResult(self.name, item)
                    if result.is_valid():
                        valid_results.append(result.to_dict())
                except Exception as e:
                    print(f"[{self.name}] Invalid result skipped: {e}")
            
            print(f"[{self.name}] Final: {len(valid_results)} valid results")
            return valid_results
            
        except Exception as e:
            print(f"[{self.name}] Search error: {e}")
            return []
    
    def get_status(self) -> Dict[str, Any]:
        """Status do scraper"""
        return {
            'name': self.name,
            'session_active': self.session is not None,
            'last_run': getattr(self, '_last_run', None)
        }
    
    def cleanup(self):
        """Limpa recursos"""
        if self.session:
            self.session.close()
            self.session = None
