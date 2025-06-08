import datetime

from sqlalchemy import String, BigInteger, Integer, Table, Column, ForeignKey, Float, ARRAY, DateTime, Boolean
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.orm import Mapped, mapped_column


class Base(DeclarativeBase, AsyncAttrs):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)


user_product_association = Table(
    'user_product_association',
    Base.metadata,
    Column('user_id', ForeignKey('users.id'), primary_key=True),
    Column('product_id', ForeignKey('products.id'), primary_key=True)
)


class UserModel(Base):
    __tablename__ = "users"
    telegram_id = Column(BigInteger, unique=True)
    username = Column(String, nullable=False)
    tutor = Column(BigInteger, default=None, nullable=True)
    referral = Column(BigInteger, default=None, nullable=True)
    name = Column(String, default="")
    role = Column(String, default="")
    trial_date = Column(DateTime, default=None, nullable=True)
    trial_period = Column(Boolean, default=False, nullable=True)
    partner = Column(ARRAY(BigInteger), nullable=True, default=[])

    student = relationship('StudentModel', lazy="selectin", uselist=False)
    rating = relationship('Rating', back_populates='user', lazy="selectin")
    subscribed_products = relationship(
        "ProductModel",
        secondary=user_product_association,
        back_populates="subscribers",
        lazy="selectin"
    )


class PartnerModel(Base):
    __tablename__ = 'partner'

    telegram_id = Column(BigInteger, unique=True)
    refs = Column(Integer, default=0)
    sum = Column(Integer, default=0)
    earn = Column(Integer, default=0)



class StudentModel(Base):
    __tablename__ = 'student'

    telegram_id = Column(BigInteger, ForeignKey('users.telegram_id'))
    refs = Column(Integer, default=0)
    balls = Column(Integer, default=0)


class ProductModel(Base):
    __tablename__ = "products"
    product_type = Column(String, nullable=False)
    subject = mapped_column(String, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, default="")
    price = Column(Float, nullable=False)
    lessons_quantity = Column(Integer, nullable=False)

    subscribers = relationship(
        "UserModel",
        secondary=user_product_association,
        back_populates="subscribed_products",
        lazy="selectin"
    )


class Rating(Base):
    __tablename__ = 'rating'
    telegram_id = Column(BigInteger, ForeignKey('users.telegram_id'))
    balls = Column(Integer, nullable=False, default=0)
    subject = Column(String, nullable=False)
    level = Column(Integer, default=1)
    user = relationship('UserModel', back_populates='rating', lazy="selectin")

    homeworks = relationship('Homeworks', back_populates='place', lazy="selectin")


class Homeworks(Base):
    __tablename__ = 'homeworks'
    rating_id = Column(ForeignKey('rating.id', ondelete='CASCADE'))
    balls = Column(Integer, nullable=False)
    subject = Column(String, nullable=False)

    place = relationship('Rating', back_populates='homeworks', lazy="selectin")


class CounterTable(Base):
    __tablename__ = 'counter'
    promos = Column(Integer, default=0)
