#!/usr/bin/env python3
# aggregate_variants_to_file.py

import os
import json
import redis

def aggregate_variants(redis_host="127.0.0.1", redis_port=6379):
    """
    Собирает из Redis все ответы raw_responses и агрегирует
    количество упоминаний каждого варианта внутри каждого канона.
    """
    r = redis.Redis(host=redis_host, port=redis_port, db=0, decode_responses=True)
    raw = r.hgetall("raw_responses")

    agg = {}
    for chunk_id, payload in raw.items():
        try:
            data = json.loads(payload)
        except json.JSONDecodeError:
            continue
        for canon, variants in data.items():
            # Если модель вернула плоский int, преобразуем в вариант=канон
            if isinstance(variants, int):
                agg.setdefault(canon, {})
                agg[canon][canon] = agg[canon].get(canon, 0) + variants
            elif isinstance(variants, dict):
                agg.setdefault(canon, {})
                for variant, cnt in variants.items():
                    agg[canon][variant] = agg[canon].get(variant, 0) + int(cnt)
    return agg

def main():
    # Чтение переменных окружения, если нужно
    redis_host = os.getenv("REDIS_HOST", "127.0.0.1")
    redis_port = int(os.getenv("REDIS_PORT", 6379))

    agg = aggregate_variants(redis_host, redis_port)
    out_path = "aggregated_variants.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(agg, f, ensure_ascii=False, indent=2)

    print(f"✅ Агрегированные варианты записаны в {out_path}")

if __name__ == "__main__":
    main()
