import json
from typing import Literal, Optional
import redis.asyncio as redis
from sqlalchemy import select, insert

from .connection import async_session_maker
from .models import UserModel, ProductModel

redis_client = redis.Redis(
    host='localhost',
    password="QLa<KA9mvh8^/q",
    username="user"
)


async def get_user_products(telegram_id: int):
    async with async_session_maker() as session:
        user = await session.execute(select(UserModel).where(UserModel.telegram_id == telegram_id))
        user = user.scalar_one_or_none()
        return user.subscribed_products


async def add_product_to_user(telegram_id: int, subject: str):
    async with async_session_maker() as session:
        get_product_stmt = await session.execute(select(ProductModel).where(ProductModel.subject == subject))
        product = get_product_stmt.scalar_one_or_none()
        user = await session.execute(select(UserModel).where(UserModel.telegram_id == telegram_id))
        user = user.scalar_one_or_none()
        if user and product:
            user.subscribed_products.append(product)
            await session.commit()


async def registrate_user(telegram_id: int, username: str):
    async with async_session_maker() as session:
        new_user = UserModel(telegram_id=telegram_id, username=username)
        session.add(new_user)
        await session.commit()

        cache_key = f"user:{telegram_id}"
        user_data = serialize_user(new_user)
        await redis_client.set(cache_key, json.dumps(user_data), ex=3600)


async def is_user_exist(telegram_id, user_name):
    async with async_session_maker() as session:
        check = await session.execute(select(UserModel).where(UserModel.telegram_id == telegram_id))
        user = check.scalar_one_or_none()

        if user:
            if user.username != user_name:
                user.username = user_name
                await session.commit()
                cache_key = f"user:{telegram_id}"
                user_data = serialize_user(user)
                await redis_client.set(cache_key, json.dumps(user_data), ex=3600)

        return user


def serialize_user(user: UserModel) -> dict:
    return {
        "id": user.id,
        "telegram_id": user.telegram_id,
        "username": user.username,
        "name": user.name,
        "role": user.role,
        #"subscribed_products": [product.id for product in user.subscribed_products]
    }


def deserialize_user(data: dict) -> UserModel:
    user = UserModel(
        id=data["id"],
        telegram_id=data["telegram_id"],
        username=data["username"],
        name=data["name"],
        role=data["role"]
    )
    return user


# Основная функция с кэшированием
async def get_user_data(telegram_id: int) -> Optional[UserModel]:
    cache_key = f"user:{telegram_id}"
    cached_user = await redis_client.get(cache_key)

    if cached_user:
        user_data = json.loads(cached_user)
        return deserialize_user(user_data)

    async with async_session_maker() as session:

        user_stmt = await session.execute(select(UserModel).where(UserModel.telegram_id == telegram_id))
        user = user_stmt.scalar_one_or_none()
        if user:
            user_data = serialize_user(user)
            await redis_client.set(cache_key, json.dumps(user_data), ex=3600)

        return user


async def update_user_name(telegram_id: int, new_name: str):
    async with async_session_maker() as session:
        user_stmt = await session.execute(select(UserModel).where(UserModel.telegram_id == telegram_id))
        user = user_stmt.scalar_one_or_none()

        if user:
            user.name = new_name
            await session.commit()

            cache_key = f"user:{telegram_id}"
            user_data = serialize_user(user)
            await redis_client.set(cache_key, json.dumps(user_data), ex=3600)

            return user


async def update_user_role(telegram_id: int,
                           new_role: Literal["student", "teacher", "confirmed_teacher", "confirmed_student"]):
    async with async_session_maker() as session:
        user_stmt = await session.execute(select(UserModel).where(UserModel.telegram_id == telegram_id))
        user = user_stmt.scalar_one_or_none()

        if user:
            user.role = new_role
            await session.commit()

            cache_key = f"user:{telegram_id}"
            user_data = serialize_user(user)
            await redis_client.set(cache_key, json.dumps(user_data), ex=3600)

            return user


async def is_user_not_exist_registrate(telegram_id: int, username: str):
    async with async_session_maker() as session:
        user = await session.execute(select(UserModel).filter(UserModel.telegram_id == telegram_id))
        existing_user = user.scalar()

        if existing_user is None:
            await registrate_user(telegram_id, username)
        else:
            cache_key = f"user:{telegram_id}"
            user_data = serialize_user(existing_user)
            await redis_client.set(cache_key, json.dumps(user_data), ex=3600)
