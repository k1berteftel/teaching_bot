import datetime
import json
from typing import Literal, Optional
import redis.asyncio as redis
from sqlalchemy import select, insert, update, delete

from .connection import async_session_maker
from .models import UserModel, ProductModel, StudentModel, Homeworks, Rating

redis_client = redis.Redis(
    host='localhost',
    password="QLa<KA9mvh8^/q",
    username="user"
)


async def update_trial_period(telegram_id: int, trial_date: datetime.datetime | None):
    async with async_session_maker() as session:
        if trial_date is not None:
            await session.execute(update(UserModel).where(UserModel.telegram_id == telegram_id).values(
                trial_date=trial_date,
                trial_period=True
            ))
        else:
            await session.execute(update(UserModel).where(UserModel.telegram_id == telegram_id).values(
                trial_date=trial_date,
                trial_period=True
            ))
            await session.execute(delete(StudentModel).where(StudentModel.telegram_id == telegram_id))
            rating: Rating = await session.scalar(select(Rating).where(Rating.telegram_id == telegram_id))
            if rating:
                await session.execute(delete(Homeworks).where(Homeworks.rating_id == rating.id))
                await session.commit()
            await session.execute(delete(Rating).where(Rating.telegram_id == telegram_id))
            user: UserModel = await session.scalar(select(UserModel).where(UserModel.telegram_id == telegram_id))
            user.subscribed_products = []
        await session.commit()


async def update_user_referral(telegram_id: int, referral_id: int):
    async with async_session_maker() as session:
        user: UserModel = await session.scalar(select(UserModel).where(UserModel.telegram_id == referral_id))
        if not user.student:
            await add_ref_model(referral_id)
    async with async_session_maker() as session:
        await session.execute(update(UserModel).where(UserModel.telegram_id == telegram_id).values(
            referral=referral_id
        ))
        await session.execute(update(StudentModel).where(StudentModel.telegram_id == referral_id).values(
            refs=StudentModel.refs + 1
        ))
        await session.commit()


async def get_user_balls(telegram_id: int):
    async with async_session_maker() as session:
        user: StudentModel = await session.scalar(select(StudentModel).where(StudentModel.telegram_id == telegram_id))
    return user if user else await add_ref_model(telegram_id)


async def add_ref_model(telegram_id: int):
    async with async_session_maker() as session:
        user: UserModel = await session.scalar(select(UserModel).where(UserModel.telegram_id == telegram_id))
        referral = StudentModel(
            telegram_id=telegram_id,
        )
        user.student = referral
        session.add(referral)
        await session.commit()
        return referral


async def add_user_balls(telegram_id: int, balls: int):
    async with async_session_maker() as session:
        user: UserModel = await session.scalar(select(UserModel).where(UserModel.telegram_id == telegram_id))
        if not user.student:
            await add_ref_model(telegram_id)
        await session.execute(update(StudentModel).where(StudentModel.telegram_id == telegram_id).values(
            balls=StudentModel.balls + balls
        ))
        await session.execute(update(Rating).where(Rating.telegram_id == telegram_id).values(
            balls=Rating.balls + balls
        ))
        await session.commit()


async def reset_user_products(telegram_id: int) -> None:
    async with async_session_maker() as session:
        user: UserModel = await session.scalar(select(UserModel).where(UserModel.telegram_id == telegram_id))
        user.subscribed_products = []
        await session.commit()


async def reset_user_partners(telegram_id: int):
    async with async_session_maker() as session:
        user = await session.execute(select(UserModel).where(UserModel.telegram_id == telegram_id))
        user = user.scalar_one_or_none()
        datas = []
        if user.partner:
            for asso in user.partner:
                partner_id: int = asso[1]
                await session.execute(update(UserModel).where(UserModel.telegram_id == partner_id).values(
                    partner=[]
                ))
        await session.execute(update(UserModel).where(UserModel.telegram_id == telegram_id).values(
            partner=[]
        ))
        await session.commit()


async def get_user_partners(telegram_id: int) -> list[dict] | None:
    async with async_session_maker() as session:
        user = await session.execute(select(UserModel).where(UserModel.telegram_id == telegram_id))
        user = user.scalar_one_or_none()
        datas = []
        if user.partner:
            for asso in user.partner:
                teacher_id: int = asso[1]
                teacher = await session.execute(select(UserModel).where(UserModel.telegram_id == teacher_id))
                teacher = teacher.scalar_one_or_none()
                for product in user.subscribed_products:
                    if product.subject in [prd.subject for prd in teacher.subscribed_products]:
                        datas.append({
                            'user_id': teacher_id,
                            'name': teacher.name,
                            'subject': product.subject
                        })
        return datas if datas else None


async def add_partner_to_user(user_id: int, partner_id: int):
    async with async_session_maker() as session:
        user = await session.execute(select(UserModel).where(UserModel.telegram_id == user_id))
        user = user.scalar_one_or_none()
        partner = user.partner if user.partner else [[user_id, partner_id]]
        if user.partner and [user.telegram_id, partner_id] not in user.partner:
            user.partner.append([user.telegram_id, partner_id])
            partner = user.partner
        print(partner)
        await session.execute(update(UserModel).where(UserModel.telegram_id == user_id).values(
            partner=partner
        ))
        await session.commit()
        cache_key = f"user:{user.telegram_id}"
        user_data = serialize_user(user)
        await redis_client.set(cache_key, json.dumps(user_data), ex=3600)


async def get_all_users() -> list[UserModel]:
    async with async_session_maker() as session:
        users = await session.scalars(select(UserModel))
        return users.fetchall()


async def get_user_by_username(username: str) -> UserModel | None:
    async with async_session_maker() as session:
        user = await session.execute(select(UserModel).where(UserModel.username == username))
        user = user.scalar_one_or_none()
        return user


async def get_user_products(telegram_id: int) -> list[ProductModel]:
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
        cache_key = f"user:{telegram_id}"
        user_data = serialize_user(user)
        await redis_client.set(cache_key, json.dumps(user_data), ex=3600)


async def registrate_user(telegram_id: int, username: str):
    async with async_session_maker() as session:
        new_user = UserModel(telegram_id=telegram_id, username=username)
        session.add(new_user)
        await session.commit()

        cache_key = f"user:{telegram_id}"
        user_data = serialize_user(new_user)
        await redis_client.set(cache_key, json.dumps(user_data), ex=3600)


async def is_user_exist(telegram_id: int, user_name):
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
        "partner": user.partner
        #"subscribed_products": [product.id for product in user.subscribed_products]
    }


def deserialize_user(data: dict) -> UserModel:
    user = UserModel(
        id=data["id"],
        telegram_id=data["telegram_id"],
        username=data["username"],
        name=data["name"],
        role=data["role"],
        partner=data["partner"]
    )
    return user


# Основная функция с кэшированием
async def get_user_data(telegram_id: int) -> Optional[UserModel]:
    #cache_key = f"user:{telegram_id}"
    #cached_user = await redis_client.get(cache_key)

    #if cached_user:
        #user_data = json.loads(cached_user)
        #return deserialize_user(user_data)

    async with async_session_maker() as session:

        user_stmt = await session.execute(select(UserModel).where(UserModel.telegram_id == telegram_id))
        user = user_stmt.scalar_one_or_none()
        #if user:
            #user_data = serialize_user(user)
            #await redis_client.set(cache_key, json.dumps(user_data), ex=3600)

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
                           new_role: Literal["student", "trial_student", "teacher", "confirmed_teacher", "confirmed_student"]):
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
