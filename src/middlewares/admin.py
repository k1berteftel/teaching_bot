from os import getenv
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message
from dotenv import load_dotenv

load_dotenv()

ADMINS = getenv('ADMINS')


class AdminMiddleware(BaseMiddleware):
    def __init__(self):
        self.admin_ids = [int(admin_id) if admin_id else ... for admin_id in list(ADMINS.split(','))]
        super().__init__()

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        if event.from_user.id in self.admin_ids:
            return await handler(event, data)
        else:
            pass
