import asyncio
from .config import MODEL_CONFIG

from src.loader import client

'''
{"role": "system",
                 "content": "Ты интервьюер. 
                 Ты должен проверить на сколько хорошо человек знает свой предмет, вопросы которые ты задаешь должны быть по темам предмета. 
                 По иностранным языкам это к примеру времена глаголов."}
'''
async def fetch_response(prompt: str):
    try:
        response = await client.chat.completions.create(
            model=MODEL_CONFIG["model"],
            messages=[
                {"role": "user", "content": prompt},
            ],
            temperature=MODEL_CONFIG["temperature"],
            max_tokens=MODEL_CONFIG["max_tokens"],
            timeout=30
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error fetching response: {e}")
        return None


async def ask_multiple(prompts):
    tasks = [fetch_response(prompt) for prompt in prompts]
    responses = await asyncio.gather(*tasks)
    return responses
