import json
from typing import Literal, Optional
import redis.asyncio as redis
from sqlalchemy import select, insert, update, and_

from .connection import async_session_maker
from .models import Rating, Homeworks, UserModel


async def create_player(telegram_id: int, subject: str) -> Rating:
    async with async_session_maker() as session:
        await session.execute(insert(Rating).values(
            telegram_id=telegram_id,
            subject=subject
        ))
        await session.commit()
        rating = await session.scalar(select(Rating).where(
            and_(
                Rating.telegram_id == telegram_id,
                Rating.subject == subject
            )
        ))
        user: UserModel = await session.scalar(select(UserModel).where(UserModel.telegram_id == telegram_id))
        user.rating.append(rating)
        await session.commit()
        return rating


async def get_rating(telegram_id: int, subject: str) -> Rating | None:
    async with async_session_maker() as session:
        rating = await session.scalar(select(Rating).where(
            and_(
                Rating.telegram_id == telegram_id,
                Rating.subject == subject
            )
        ))
    return rating


async def add_homework(telegram_id: int, balls: int, subject: str):
    async with async_session_maker() as session:
        homework = Homeworks(
            balls=balls,
            subject=subject
        )
        rating = await session.scalar(select(Rating).where(
            and_(
                Rating.telegram_id == telegram_id,
                Rating.subject == subject
            )
        ))
        rating.homeworks.append(homework)
        rating.balls += homework.balls
        await session.commit()
    await _check_level(rating)


async def get_subject_rating(subject: str) -> list[Rating]:
    async with async_session_maker() as session:
        rating = await session.scalars(select(Rating).where(Rating.subject == subject).order_by(Rating.balls))
    return rating.fetchall()


async def _check_level(rating: Rating) -> None:
    level = rating.level
    balls = rating.balls
    if level == 1:
        if balls not in range(0, 70):
            await _set_rating_level(rating, 2)
    elif level == 2:
        if balls not in range(70, 200):
            await _set_rating_level(rating, 3)
    elif level == 3:
        if balls not in range(200, 400):
            await _set_rating_level(rating, 4)
    elif level == 4:
        if balls not in range(400, 650):
            await _set_rating_level(rating, 5)
    elif level == 5:
        if balls not in range(650, 950):
            await _set_rating_level(rating, 6)
    elif level == 6:
        if balls not in range(950, 1300):
            await _set_rating_level(rating, 7)
    elif level == 7:
        if balls not in range(1300, 1700):
            await _set_rating_level(rating, 8)
    elif level == 8:
        if balls not in range(1700, 2150):
            await _set_rating_level(rating, 9)
    elif level == 9:
        if balls not in range(2150, 2650):
            await _set_rating_level(rating, 10)
    elif level == 10:
        if balls not in range(2650, 3200):
            await _set_rating_level(rating, 11)
    elif level == 11:
        if balls not in range(3200, 3800):
            await _set_rating_level(rating, 12)
    elif level == 12:
        if balls not in range(3800, 4450):
            await _set_rating_level(rating, 13)
    elif level == 13:
        if balls not in range(4450, 5150):
            await _set_rating_level(rating, 14)
    elif level == 14:
        if balls not in range(5150, 5900):
            await _set_rating_level(rating, 15)
    return


async def _set_rating_level(rating: Rating, level: int):
    async with async_session_maker() as session:
        rating.level = level
        await session.commit()
