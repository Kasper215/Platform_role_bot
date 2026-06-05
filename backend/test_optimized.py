"""Quick test of the updated NSFW system with improved prompts."""
import asyncio
import sys
sys.path.insert(0, "backend")

from llm_client import get_bot_reply

PERSONA = """Ты — Алиса, загадочная и обворожительная девушка 22 лет.
Длинные тёмные волосы, зелёные глаза, стройная фигура.
Любит флиртовать, дразнить, уверена в себе.
Говорит живым разговорным языком, 2-4 предложения.
Описывает свои физические действия и ощущения подробно."""

async def test():
    results = []

    results.append("=" * 60)
    results.append("TEST 1: Флирт + контекст действий")
    results.append("=" * 60)

    history = [
        {"role": "assistant", "content": "*откидывает волосы назад* Привет~ Ну и что ты тут забыл?"},
        {"role": "user", "content": "ты красивая"},
        {"role": "assistant", "content": "*улыбается и наклоняет голову* Спасибо~ Ты тоже ничего так"},
    ]

    reply = await get_bot_reply(
        system_prompt=PERSONA,
        history=history,
        user_message="*обнимает тебя за талию* иди ко мне",
        bot_name="Алиса",
        is_nsfw=True
    )
    results.append(f"\nОтвет:\n{reply}\n")

    results.append("=" * 60)
    results.append("TEST 2: Более откровенный контекст")
    results.append("=" * 60)

    history2 = [
        {"role": "assistant", "content": "*прижимается ближе* Мм, мне нравится..."},
        {"role": "user", "content": "сними рубашку"},
    ]

    reply2 = await get_bot_reply(
        system_prompt=PERSONA,
        history=history2,
        user_message="покажи",
        bot_name="Алиса",
        is_nsfw=True
    )
    results.append(f"\nОтвет:\n{reply2}\n")

    # Save results to file
    with open("backend/test_results.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(results))
    
    print("Results saved to backend/test_results.txt")

asyncio.run(test())
