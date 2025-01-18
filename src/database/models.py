from sqlalchemy import String, BigInteger, Integer, Table, Column, ForeignKey, Float
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
    telegram_id = Column(BigInteger)
    username = Column(String, nullable=False)
    name = Column(String, default="")
    role = Column(String, default="")

    subscribed_products = relationship(
        "ProductModel",
        secondary=user_product_association,
        back_populates="subscribers",
        lazy="selectin"
    )


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
