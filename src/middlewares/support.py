from aiogram import BaseMiddleware
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from typing import Callable, Dict, Any, Awaitable
from src.handlers.fsm_models import Interview


class GroupCallbackMiddleware(BaseMiddleware):
    def __init__(self, group_id_student: int, group_id_teacher: int, group_id_recruiter: int, group_id_application: int,
                 allowed_callback_data: set):
        super().__init__()
        self.group_id_student = group_id_student
        self.group_id_teacher = group_id_teacher
        self.group_id_recruiter = group_id_recruiter
        self.group_id_application = group_id_application
        self.allowed_callback_data = allowed_callback_data

    async def __call__(self,
                       handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
                       event: Any,
                       data: Dict[str, Any]) -> Any:
        # Проверяем тип события и обрабатываем для CallbackQuery
        if isinstance(event, CallbackQuery):
            chat_id = event.message.chat.id
            callback_data = event.data
            if chat_id == self.group_id_recruiter or chat_id == self.group_id_application:
                if callback_data in self.allowed_callback_data or callback_data.startswith("candidate|") or callback_data.startswith('teacher|'):
                    return await handler(event, data)
            return await handler(event, data)


class GroupMessageMiddleware(BaseMiddleware):
    def __init__(self, group_id_student: int, group_id_teacher: int, group_id_recruiter: int, group_id_methodical: int, group_id_technical: int):
        super().__init__()
        self.group_id_student = group_id_student
        self.group_id_teacher = group_id_teacher
        self.group_id_recruiter = group_id_recruiter
        self.group_id_methodical = group_id_methodical
        self.group_id_technical = group_id_technical

    async def __call__(self,
                       handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
                       event: Any,
                       data: Dict[str, Any]) -> Any:
        if isinstance(event, Message):
            print("Instance")
            chat_id = event.chat.id
            state: FSMContext = data.get('state')

            # Логика для команд и сообщений в личных сообщениях
            if chat_id == event.from_user.id:
                if event.text != "/id":
                    return await handler(event, data)
            elif event.text == "/id":
                return await handler(event, data)

            # Логика для сообщений, адресованных боту, в группах студентов и преподавателей
            if ((chat_id == self.group_id_student) or (chat_id == self.group_id_teacher) or (chat_id == self.group_id_methodical) or (chat_id == self.group_id_technical)) and (
                    event.reply_to_message and event.reply_to_message.from_user.id == (await event.bot.me()).id):
                return await handler(event, data)

            # Логика для сообщений в группе рекрутеров, если пользователь находится в нужном состоянии FSM
            if chat_id == self.group_id_recruiter:
                if (await state.get_state()) == Interview.feed_back_comment:
                    return await handler(event, data)

            if (chat_id in [self.group_id_methodical, self.group_id_recruiter, self.group_id_student, self.group_id_teacher]
                    and event.text.startswith('/send_message')):
                return await handler(event, data)

        return None
