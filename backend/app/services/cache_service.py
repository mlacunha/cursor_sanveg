import json
import os
import redis
from typing import Optional

class CacheService:
    """
    Serviço para gerenciar o cache de respostas da API no Redis.
    Focado em evitar requisições repetitivas ao banco de dados para a mesma área geográfica.
    """
    def __init__(self):
        redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
        try:
            self.redis = redis.from_url(redis_url, decode_responses=True)
            self.enabled = True
        except Exception as e:
            print(f"Aviso: Não foi possível conectar ao Redis ({e}). Cache desativado.")
            self.enabled = False

    def get_bbox_cache(self, prefix: str, bbox: str) -> Optional[dict]:
        """
        Tenta recuperar um GeoJSON cacheado para um determinado BBox.
        """
        if not self.enabled:
            return None
        
        key = f"{prefix}:bbox:{bbox}"
        cached_data = self.redis.get(key)
        if cached_data:
            return json.loads(cached_data)
        return None

    def set_bbox_cache(self, prefix: str, bbox: str, data: dict, ttl: int = 2592000):
        """
        Salva o GeoJSON no Redis com um TTL padrão de 30 dias (2592000 segundos).
        """
        if not self.enabled:
            return
        
        key = f"{prefix}:bbox:{bbox}"
        self.redis.setex(key, ttl, json.dumps(data))

# Instância única para uso em toda a aplicação
cache_service = CacheService()
