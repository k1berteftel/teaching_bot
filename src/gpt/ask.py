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


async def get_assistant_and_thread():
    """
    :return: Две str переменной по факту являющиеся уникальными для каждого юзера, чтобы обрабатывать их
        диалог отдельно от других юзеров
    """
    role = ('Тебя зовут Макс и ты виртуальный помощник онлайн школы "easyknow", твоя задача -'
            'помогать ученику выполнять домашнее задание')
    assistant = await client.beta.assistants.create(
        model=MODEL_CONFIG["model"],
        instructions=role,
    )
    thread = await client.beta.threads.create()
    return assistant.id, thread.id


async def get_text_answer(text: str, assistant_id: str, thread_id: str) -> str | None:
    """
        Обработка ИИшкой сообщения юзера, возвращает ответ ИИ
    """
    print(assistant_id, thread_id)
    message = await client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=text
    )
    run = await client.beta.threads.runs.create_and_poll(
        thread_id=thread_id,
        assistant_id=assistant_id
    )
    if run.status == "completed":
        messages = await client.beta.threads.messages.list(thread_id=thread_id)
        print(messages)

        async for message in messages:
            print(message.content[0].text.value)
            return message.content[0].text.value
    else:
        return None


async def delete_assistant_and_thread(assistant_id: str, thread_id: str):
    """
        Удаление ассистента и потока (после окончательного завершения диалога с юзером)
    """
    await client.beta.assistants.delete(assistant_id)
    await client.beta.threads.delete(thread_id)
