import json
from typing import Literal, Optional
import redis.asyncio as redis
from sqlalchemy import select, insert, update

from .connection import async_session_maker
from .models import UserModel, PartnerModel


async def add_partner(telegram_id: int) -> PartnerModel:
    async with async_session_maker() as session:
        await session.execute(insert(PartnerModel).values(telegram_id=telegram_id))
        await session.commit()
        partner = await session.scalar(select(PartnerModel).where(PartnerModel.telegram_id == telegram_id))
    return partner


async def get_partners() -> list[PartnerModel]:
    async with async_session_maker() as session:
        partners = await session.scalars(select(PartnerModel).order_by(PartnerModel.earn))
    return list(partners)


async def get_partner_data(telegram_id: int) -> PartnerModel:
    async with async_session_maker() as session:
        partner = await session.scalar(select(PartnerModel).where(PartnerModel.telegram_id == telegram_id))
    return partner if partner else await add_partner(telegram_id)


async def add_refs(partner_id: int, telegram_id: int):
    async with async_session_maker() as session:
        await session.execute(update(UserModel).where(UserModel.telegram_id == telegram_id).values(
            tutor=partner_id
        ))
        await session.execute(update(PartnerModel).where(PartnerModel.telegram_id == partner_id).values(
            refs=PartnerModel.refs + 1
        ))
        await session.commit()


async def add_partner_earn(partner_id: int, sum: int):
    async with async_session_maker() as session:
        earn = int(round(sum * 0.05))
        await session.execute(update(PartnerModel).where(PartnerModel.telegram_id == partner_id).values(
            sum=PartnerModel.sum + sum,
            earn=PartnerModel.earn + earn
        ))
        await session.commit()