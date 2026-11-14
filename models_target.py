from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import Index
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class TargetBase(DeclarativeBase):
    pass


class DimDate(TargetBase):
    __tablename__ = "dim_date"
    date_key: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[date]
    year: Mapped[int]
    quarter: Mapped[int]
    month: Mapped[int]
    day_of_month: Mapped[int]
    day_of_week: Mapped[int]
    is_weekend: Mapped[int]


class DimFilm(TargetBase):
    __tablename__ = "dim_film"
    film_key: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    film_id: Mapped[int] = mapped_column(unique=True)
    title: Mapped[str]
    rating: Mapped[Optional[str]]
    length: Mapped[Optional[int]]
    language: Mapped[str]
    release_year: Mapped[Optional[int]]
    last_update: Mapped[datetime]


class DimActor(TargetBase):
    __tablename__ = "dim_actor"
    actor_key: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    actor_id: Mapped[int] = mapped_column(unique=True)
    first_name: Mapped[str]
    last_name: Mapped[str]
    last_update: Mapped[datetime]


class DimCategory(TargetBase):
    __tablename__ = "dim_category"
    category_key: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    category_id: Mapped[int] = mapped_column(unique=True)
    name: Mapped[str]
    last_update: Mapped[datetime]


class DimStore(TargetBase):
    __tablename__ = "dim_store"
    store_key: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    store_id: Mapped[int] = mapped_column(unique=True)
    city: Mapped[str]
    country: Mapped[str]
    last_update: Mapped[datetime]


class DimCustomer(TargetBase):
    __tablename__ = "dim_customer"
    customer_key: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    customer_id: Mapped[int] = mapped_column(unique=True)
    first_name: Mapped[str]
    last_name: Mapped[str]
    active: Mapped[int]
    city: Mapped[str]
    country: Mapped[str]
    last_update: Mapped[datetime]


class BridgeFilmActor(TargetBase):
    __tablename__ = "bridge_film_actor"
    film_key: Mapped[int] = mapped_column(primary_key=True)
    actor_key: Mapped[int] = mapped_column(primary_key=True)


class BridgeFilmCategory(TargetBase):
    __tablename__ = "bridge_film_category"
    film_key: Mapped[int] = mapped_column(primary_key=True)
    category_key: Mapped[int] = mapped_column(primary_key=True)


class FactRental(TargetBase):
    __tablename__ = "fact_rental"
    fact_rental_key: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    rental_id: Mapped[int] = mapped_column(unique=True)
    date_key_rented: Mapped[int]
    date_key_returned: Mapped[Optional[int]]
    film_key: Mapped[int]
    store_key: Mapped[int]
    customer_key: Mapped[int]
    staff_id: Mapped[int]
    rental_duration_days: Mapped[Optional[int]]
    __table_args__ = (
        Index("ix_fact_rental_date_rented", "date_key_rented"),
        Index("ix_fact_rental_date_returned", "date_key_returned"),
        Index("ix_fact_rental_film", "film_key"),
        Index("ix_fact_rental_store", "store_key"),
        Index("ix_fact_rental_customer", "customer_key"),
    )


class FactPayment(TargetBase):
    __tablename__ = "fact_payment"
    fact_payment_key: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    payment_id: Mapped[int] = mapped_column(unique=True)
    date_key_paid: Mapped[int]
    customer_key: Mapped[int]
    store_key: Mapped[int]
    staff_id: Mapped[int]
    amount: Mapped[Decimal]
    __table_args__ = (
        Index("ix_fact_payment_date", "date_key_paid"),
        Index("ix_fact_payment_customer", "customer_key"),
        Index("ix_fact_payment_store", "store_key"),
    )


class SyncState(TargetBase):
    __tablename__ = "sync_state"
    table_name: Mapped[str] = mapped_column(primary_key=True)
    last_update: Mapped[datetime]
