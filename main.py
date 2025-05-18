import json
import argparse

from llm_module import build_prompt, call_llm
from fb_read import parse_fb2, chunk_by_sentences_with_word_split
from redis_module import get_redis_client, clear_raw_responses, save_raw_response

def main(fb2_path: str, redis_host: str, redis_port: int, max_tokens: int):
    text   = parse_fb2(fb2_path)
    chunks = chunk_by_sentences_with_word_split(text, max_tokens=max_tokens)
    print(f"Найдено чанков: {len(chunks)}")
    # Оставляем только первые 10
    chunks = chunks[:10]
    print(f"Будут обработаны первые {len(chunks)} чанков")
    r = get_redis_client(host=redis_host, port=redis_port)
    clear_raw_responses(r)
    # 3) Задаём JSON Schema для структурированного вывода
    schema = {
        "name": "ner_counts",
        "strict": True,
        "schema": {
            "type": "object",
            # любой ключ верхнего уровня — объект вариантов
            "additionalProperties": {
                "type": "object",
                # любой ключ во вложенном объекте — целое число
                "additionalProperties": {
                    "type": "integer",
                    "description": "Количество упоминаний данного варианта"
                }
            }
        }
    }
    # 4) Последовательно обрабатываем каждый чанк
    for idx, chunk in enumerate(chunks):
        current_counts = {k: int(v) for k,v in r.hgetall("char_counter").items()}
        # 4.2) Формируем промпт и отправляем запрос
        messages = build_prompt(chunk, current_counts)
        result = call_llm(messages, schema)

        # 4.3) Логируем в консоль
        print(f"\n--- Чанк {idx+1}/{len(chunks)} ---")
        preview = chunk[:200] + ("…" if len(chunk) > 200 else "")
        print(preview)
        if "error" in result:
            print("Ошибка от LLM:", result["error"])
        else:
            print("Ответ LLM:", json.dumps(result, ensure_ascii=False, indent=2))
            # 4.4) Обновляем глобальный счётчик
            for canon, variants in result.items():
                total = sum(variants.values())
                r.hincrby("char_counter", canon, total)

        # 4.5) Сохраняем в raw_responses
        save_raw_response(r, idx, result)
    final = r.hgetall("char_counter")
    print("\nГотово: все чанки обработаны и сохранены в Redis.")
    print(json.dumps(final, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="LLM-NER: разбиваем FB2 на чанки, обогащаем промпт текущими счётчиками, "\
                    "получаем строго структурированный JSON и сохраняем всё в Redis."
    )
    parser.add_argument("fb2", help="путь к FB2-файлу (например book/voina-i-mir.fb2)")
    parser.add_argument("--redis-host", default="redis", help="хост Redis")
    parser.add_argument("--redis-port", type=int, default=6379, help="порт Redis")
    parser.add_argument("--max-tokens", type=int, default=2000, help="максимум токенов на чанк")
    args = parser.parse_args()

    main(
        fb2_path=args.fb2,
        redis_host=args.redis_host,
        redis_port=args.redis_port,
        max_tokens=args.max_tokens
    )