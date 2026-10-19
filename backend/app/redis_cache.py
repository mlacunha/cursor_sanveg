import json
import redis
import os
from functools import wraps
from typing import Callable, Any

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

try:
    redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
except Exception:
    redis_client = None

def cache_response(expire: int = 600):
    """
    Simples decorador para cache no Redis.
    Usa os parâmetros da func params como key, ignora `db` e classes nulas.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            if not redis_client:
                return func(*args, **kwargs)

            # Montar chave baseada no nome da função e argumentos (simples)
            # Dicionários, request, db sessões são puladas
            key_parts = [func.__name__]
            for kwarg, value in kwargs.items():
                if kwarg not in ['db', 'current_user', 'request']:
                    key_parts.append(f"{kwarg}:{value}")
            cache_key = "cache:" + ":".join(key_parts)

            cached_value = redis_client.get(cache_key)
            if cached_value:
                # O Pydantic sabe deserializar uma lista de dicionários
                return json.loads(cached_value)

            # Executa a função
            result = func(*args, **kwargs)

            # Se for model do SQLAlchemy, tenta aplicar o modo obj
            # Ou serializar para dict json-friendly (via jsonable_encoder do FastAPI)
            from fastapi.encoders import jsonable_encoder
            json_result = jsonable_encoder(result)

            redis_client.set(cache_key, json.dumps(json_result), ex=expire)
            return result
        return wrapper
    return decorator
