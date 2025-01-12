from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message

from src.database.user import is_user_exist, registrate_user


class UserCheckMiddleware(BaseMiddleware):
    async def __call__(self,
                       handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
                       event: TelegramObject,
                       data: Dict[str, Any]) -> Any:
        if isinstance(event, Message):
            user_id = event.from_user.id
            user_name = event.from_user.username
            is_exist = await is_user_exist(user_id, user_name)
            if not is_exist:
                if not user_name:
                    await event.answer(f"""
Извините, но чтобы воспользоваться ботом нужно установить имя пользователя (@)
Пожалуйста, установите имя пользователя в настройках Telegram и перезапустите бота (/start)
""")
                    return
                await registrate_user(telegram_id=user_id, username=user_name)

        return await handler(event, data)
