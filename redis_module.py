import os
import json
import redis

def get_redis_client(host: str = None, port: int = None) -> redis.Redis:
    """
    Возвращает клиента Redis.
    Параметры можно передать явно или взять из переменных окружения.
    """
    host = host or os.getenv("REDIS_HOST", "redis")
    port = port or int(os.getenv("REDIS_PORT", 6379))
    return redis.Redis(host=host, port=port, db=0, decode_responses=True)

def clear_raw_responses(r: redis.Redis) -> None:
    """
    Удаляет хэш 'raw_responses' в Redis, если он существует.
    """
    r.delete("raw_responses")

def save_raw_response(r: redis.Redis, idx: int, data: dict) -> None:
    """
    Сохраняет JSON-ответ LLM (data) в хэш 'raw_responses' под полем idx.
    """
    r.hset("raw_responses", idx, json.dumps(data, ensure_ascii=False))
    