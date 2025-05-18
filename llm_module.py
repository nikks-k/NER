import os
import requests
import json
import time
import re
from dotenv import load_dotenv

load_dotenv() 

def build_prompt(chunk: str, current_counts: dict) -> list[dict]:
    with open("./prompts/extract_names_prompt.md", "r") as file:
        system = file.read()
    user = f"Текст чанка:\n{chunk},\nPREVIOUS_JSON:\n{json.dumps(current_counts, ensure_ascii=False, indent=2)}"
    return [
        {"role": "system",  "content": system},
        {"role": "user",    "content": user}
    ]

def call_llm(messages: list[dict],
             schema: dict,
             temperature: float = 0.5
             ) -> dict:
    """
    Отправляет запрос к OpenRouter с json_schema и structured_outputs=True.
    При ошибке parsing failed: 'choices' автоматически повторяет до max_retries,
    делая паузу: 5 сек после 1-й, 10 сек после 2-й, 15 сек после 3-й попытки.
    Всегда возвращает dict: либо распарсенный JSON, либо {'error': ...}.
    """
    API_KEY = os.getenv("API_KEY")
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "deepseek/deepseek-chat-v3-0324",
        "messages": messages,
        "temperature": temperature,
        "response_format": {
            "type": "json_schema",
            "json_schema": schema
        },
        "provider":{
            "order": ["inference.net"]
        },
        "structured_outputs": True
    }

    while True:
        try:
            resp = requests.post(
                url=url,
                headers=headers,
                data=json.dumps(payload),
                timeout=60
            )
        except requests.RequestException as e:
            print(f"[Error] network request failed: {e}")
            time.sleep(10)
            continue

        if resp.status_code != 200:
            print(f"[Error] HTTP {resp.status_code}: {resp.text}")
            time.sleep(10)
            continue

        try:
            data = resp.json()
            raw  = data["choices"][0]["message"]["content"]
            print("‹RAW CONTENT›:", repr(raw))
        except Exception as e:
            print(data)
            print(f"[Error] response parsing failed: {e}")
            time.sleep(10)
            continue

        # Снимаем возможную обёртку ```json ... ```
        stripped = re.sub(r"^```(?:json)?\s*", "", raw)
        stripped = re.sub(r"\s*```$", "", stripped).strip()

        try:
            return json.loads(stripped)
        except json.JSONDecodeError as e:
            print(f"[Error] invalid JSON: {e}")
            print("‹STRIPPED CONTENT›:", repr(stripped))
            time.sleep(10)
            continue
