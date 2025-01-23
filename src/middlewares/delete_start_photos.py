from typing import Callable, Dict, Any, Awaitable, List
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from src.gpt import delete_assistant_and_thread


class DeletePhotosMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        if isinstance(event, CallbackQuery):
            state: FSMContext = data.get("state")
            if state:
                user_data = await state.get_data()

                photos_to_delete: List[int] = user_data.get("photos_to_delete", [])
                assistant_id, thread_id = user_data.get('assistant_id'), user_data.get('thread_id')

                if photos_to_delete:
                    for message_id in photos_to_delete:
                        try:
                            await event.bot.delete_message(event.from_user.id, message_id)
                        except Exception as e:
                            print(f"Ошибка при удалении сообщения {message_id}: {e}")
                    await state.update_data(photos_to_delete=[])

                if assistant_id and thread_id:
                    try:
                        await delete_assistant_and_thread(assistant_id, thread_id)
                    except Exception as e:
                        print(f"Ошибка при удалении модели ассистента и потока: {e}")
                    await state.update_data(assistant_id=None, thread_id=None)

        return await handler(event, data)
