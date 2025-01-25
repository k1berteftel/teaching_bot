import json
from typing import Literal, Optional
from sqlalchemy import select, insert, update

from .connection import async_session_maker
from .models import CounterTable


async def create_counter():
    async with async_session_maker() as session:
        await session.execute(insert(CounterTable).values(promos=0))
        await session.commit()


async def add_count():
    async with async_session_maker() as session:
        count = await session.scalar(select(CounterTable.promos))
        await session.execute(update(CounterTable).values(
            promos=int(count) + 1
        ))
        await session.commit()


async def get_count() -> int:
    async with async_session_maker() as session:
        count = await session.scalar(select(CounterTable.promos))
        print(count)
        print(type(count))
    return count