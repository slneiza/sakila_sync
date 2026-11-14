from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class SourceBase(DeclarativeBase):
    pass


class Language(SourceBase):
    __tablename__ = "language"
    language_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    last_update: Mapped[datetime]


class Film(SourceBase):
    __tablename__ = "film"
    film_id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    language_id: Mapped[int]
    release_year: Mapped[Optional[int]]
    length: Mapped[Optional[int]]
    rating: Mapped[Optional[str]]
    last_update: Mapped[datetime]


class Actor(SourceBase):
    __tablename__ = "actor"
    actor_id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str]
    last_name: Mapped[str]
    last_update: Mapped[datetime]


class Category(SourceBase):
    __tablename__ = "category"
    category_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    last_update: Mapped[datetime]


class FilmActor(SourceBase):
    __tablename__ = "film_actor"
    actor_id: Mapped[int] = mapped_column(primary_key=True)
    film_id: Mapped[int] = mapped_column(primary_key=True)
    last_update: Mapped[datetime]


class FilmCategory(SourceBase):
    __tablename__ = "film_category"
    film_id: Mapped[int] = mapped_column(primary_key=True)
    category_id: Mapped[int] = mapped_column(primary_key=True)
    last_update: Mapped[datetime]


class Inventory(SourceBase):
    __tablename__ = "inventory"
    inventory_id: Mapped[int] = mapped_column(primary_key=True)
    film_id: Mapped[int]
    store_id: Mapped[int]
    last_update: Mapped[datetime]


class Country(SourceBase):
    __tablename__ = "country"
    country_id: Mapped[int] = mapped_column(primary_key=True)
    country: Mapped[str]
    last_update: Mapped[datetime]


class City(SourceBase):
    __tablename__ = "city"
    city_id: Mapped[int] = mapped_column(primary_key=True)
    city: Mapped[str]
    country_id: Mapped[int]
    last_update: Mapped[datetime]


class Address(SourceBase):
    __tablename__ = "address"
    address_id: Mapped[int] = mapped_column(primary_key=True)
    city_id: Mapped[int]
    last_update: Mapped[datetime]


class Store(SourceBase):
    __tablename__ = "store"
    store_id: Mapped[int] = mapped_column(primary_key=True)
    address_id: Mapped[int]
    last_update: Mapped[datetime]


class Staff(SourceBase):
    __tablename__ = "staff"
    staff_id: Mapped[int] = mapped_column(primary_key=True)
    store_id: Mapped[int]
    last_update: Mapped[datetime]


class Customer(SourceBase):
    __tablename__ = "customer"
    customer_id: Mapped[int] = mapped_column(primary_key=True)
    store_id: Mapped[int]
    first_name: Mapped[str]
    last_name: Mapped[str]
    address_id: Mapped[int]
    active: Mapped[int]
    last_update: Mapped[datetime]


class Rental(SourceBase):
    __tablename__ = "rental"
    rental_id: Mapped[int] = mapped_column(primary_key=True)
    rental_date: Mapped[datetime]
    inventory_id: Mapped[int]
    customer_id: Mapped[int]
    return_date: Mapped[Optional[datetime]]
    staff_id: Mapped[int]
    last_update: Mapped[datetime]


class Payment(SourceBase):
    __tablename__ = "payment"
    payment_id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int]
    staff_id: Mapped[int]
    rental_id: Mapped[Optional[int]]
    amount: Mapped[Decimal]
    payment_date: Mapped[datetime]
    last_update: Mapped[datetime]
