import datetime
import random

from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from src.database import get_user_data, update_trial_period, add_user_balls


async def student_trial_period(user_id: int, bot: Bot, scheduler: AsyncIOScheduler):
    user = await get_user_data(user_id)
    if not user.trial_date or user.trial_date.timestamp() < datetime.datetime.today().timestamp():
        await update_trial_period(user_id, None)
        text = ('<b>🌟 Уважаемый пользователь! 🌟</b>\n\n<b>⏱️ Время пробного периода подошло к концу.</b>\n'
                'Мы рады, что вы смогли познакомиться с функционалом нашей онлайн-школы и оценить все преимущества '
                'обучения у нас. Надеемся, что эти 5 дней принесли вам не только новые знания, но и '
                'вдохновение для дальнейшего роста!\n\n<b>💡 А теперь самое время сделать следующий шаг!</b>\n'
                'Присоединяйтесь к нам на полный курс обучения и раскройте весь свой потенциал. '
                'Наши программы созданы для тех, кто готов учиться, развиваться и достигать новых высот.')
        await bot.send_message(
            chat_id=user_id,
            text=text
        )
        job = scheduler.get_job(job_id=f'trial_period_{user_id}')
        if job:
            job.remove()
        return
    balls = random.randint(5, 20)
    await add_user_balls(user_id, balls)
    text = (f'<b>Вы получили +{balls} баллов за регулярность ! 🎉</b>\n\n'
            f'Мы ценим ваше стремление учиться каждый день и рады, что вы продолжаете двигаться к своим целям.\n\n'
            f'<b>💡 Важно</b>: В рамках пробного периода баллы за регулярность начисляются автоматически. '
            f'Однако после перехода на полноценное обучение такие бонусы будут начислять ваши учителя вручную. '
            f'Это позволит сделать систему более гибкой и персонализированной для каждого ученика.\n\n'
            f'<b>🎯 Продолжайте в том же духе!</b> Регулярность — ключ к успеху, и мы уверены, что вы '
            f'добьетесь отличных результатов.')
    await bot.send_message(
        chat_id=user_id,
        text=text
    )