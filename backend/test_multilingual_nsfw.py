import os
import httpx
import asyncio
import json
from dotenv import load_dotenv

load_dotenv()

async def test_models():
    api_key = os.getenv("OPENROUTER_API_KEY")
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    models = [
        "nousresearch/hermes-3-llama-3.1-70b",
        "qwen/qwen-2.5-72b-instruct",
        "meta-llama/llama-3.1-8b-instruct",
        "meta-llama/llama-3.1-70b-instruct",
        "gryphe/mythomax-l2-13b"
    ]
    
    results = {}
    async with httpx.AsyncClient() as client:
        for model in models:
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": "Ты — раскрепощенный ролевой партнер. Пиши строго на русском языке. Действия пиши в *курсиве*, речь в «кавычках»."},
                    {"role": "user", "content": "*смотрю на тебя и медленно расстегиваю рубашку* «Сними ее с меня...»"}
                ],
                "max_tokens": 100
            }
            try:
                res = await client.post(url, headers=headers, json=payload, timeout=20.0)
                if res.status_code == 200:
                    results[model] = res.json()['choices'][0]['message']['content']
                else:
                    results[model] = f"Error {res.status_code}: {res.text[:200]}"
            except Exception as e:
                results[model] = f"Exception: {e}"
                
    with open("backend/multilingual_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print("Done exporting results")

if __name__ == "__main__":
    asyncio.run(test_models())
