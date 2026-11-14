import logging
from datetime import datetime, timedelta

from sqlalchemy import func, select

from config import SourceSession, TargetSession, target_engine
import models_source as s
import models_target as t

log = logging.getLogger(__name__)
EPOCH = datetime(1970, 1, 1)

MODELS = {
    "language": s.Language, "film": s.Film, "actor": s.Actor,
    "category": s.Category, "film_actor": s.FilmActor,
    "film_category": s.FilmCategory, "inventory": s.Inventory,
    "store": s.Store, "staff": s.Staff, "customer": s.Customer,
    "address": s.Address, "city": s.City, "country": s.Country,
    "rental": s.Rental, "payment": s.Payment,
}


def date_key(d):
    return int(d.strftime("%Y%m%d"))


def add_date(tgt, d):
    # d is a date; add it to dim_date if it isn't there yet
    if tgt.scalar(select(t.DimDate).where(t.DimDate.date_key == date_key(d))):
        return
    dow = d.isoweekday()  # Monday = 1, Sunday = 7
    tgt.add(t.DimDate(
        date_key=date_key(d), date=d, year=d.year,
        quarter=(d.month - 1) // 3 + 1, month=d.month, day_of_month=d.day,
        day_of_week=dow, is_weekend=1 if dow >= 6 else 0))


def save(tgt, model, id_name, data):
    # update the row if it exists, otherwise insert it
    row = tgt.scalar(select(model).where(getattr(model, id_name) == data[id_name]))
    if row is None:
        tgt.add(model(**data))
    else:
        for name, value in data.items():
            setattr(row, name, value)


def place(src, address_id):
    address = src.get(s.Address, address_id)
    city = src.get(s.City, address.city_id)
    country = src.get(s.Country, city.country_id)
    return city.city, country.country


def run_init():
    t.TargetBase.metadata.create_all(target_engine)
    with SourceSession() as src, TargetSession.begin() as tgt:
        dates = [
            src.scalar(select(func.min(s.Rental.rental_date))),
            src.scalar(select(func.max(s.Rental.return_date))),
            src.scalar(select(func.min(s.Payment.payment_date))),
            src.scalar(select(func.max(s.Payment.payment_date))),
        ]
        day = min(d for d in dates if d).date()
        last = max(d for d in dates if d).date()
        while day <= last:
            add_date(tgt, day)
            day += timedelta(days=1)
        for name in MODELS:
            if tgt.get(t.SyncState, name) is None:
                tgt.add(t.SyncState(table_name=name, last_update=EPOCH))
    log.info("tables created, dim_date and sync_state ready")


def run_sync(full):
    with SourceSession() as src, TargetSession.begin() as tgt:
        # where did we stop last time? (full load starts from 1970)
        old = {}
        for name in MODELS:
            state = tgt.get(t.SyncState, name)
            old[name] = EPOCH if full or state is None else state.last_update

        # ---- dimensions ----
        for f in src.scalars(select(s.Film).where(s.Film.last_update >= old["film"])).all():
            language = src.get(s.Language, f.language_id).name
            save(tgt, t.DimFilm, "film_id", dict(
                film_id=f.film_id, title=f.title, rating=f.rating, length=f.length,
                language=language, release_year=f.release_year,
                last_update=f.last_update))

        for a in src.scalars(select(s.Actor).where(s.Actor.last_update >= old["actor"])).all():
            save(tgt, t.DimActor, "actor_id", dict(
                actor_id=a.actor_id, first_name=a.first_name,
                last_name=a.last_name, last_update=a.last_update))

        for c in src.scalars(select(s.Category).where(s.Category.last_update >= old["category"])).all():
            save(tgt, t.DimCategory, "category_id", dict(
                category_id=c.category_id, name=c.name, last_update=c.last_update))

        # stores and customers: reload all every time, so address/city/country
        # changes get picked up
        for st in src.scalars(select(s.Store)).all():
            city, country = place(src, st.address_id)
            save(tgt, t.DimStore, "store_id", dict(
                store_id=st.store_id, city=city, country=country,
                last_update=st.last_update))

        for c in src.scalars(select(s.Customer)).all():
            city, country = place(src, c.address_id)
            save(tgt, t.DimCustomer, "customer_id", dict(
                customer_id=c.customer_id, first_name=c.first_name,
                last_name=c.last_name, active=c.active, city=city,
                country=country, last_update=c.last_update))

        tgt.flush()
        film_key = {r.film_id: r.film_key for r in tgt.scalars(select(t.DimFilm))}
        actor_key = {r.actor_id: r.actor_key for r in tgt.scalars(select(t.DimActor))}
        category_key = {r.category_id: r.category_key for r in tgt.scalars(select(t.DimCategory))}
        store_key = {r.store_id: r.store_key for r in tgt.scalars(select(t.DimStore))}
        customer_key = {r.customer_id: r.customer_key for r in tgt.scalars(select(t.DimCustomer))}

        # ---- bridges ----
        for fa in src.scalars(select(s.FilmActor).where(s.FilmActor.last_update >= old["film_actor"])).all():
            ids = (film_key[fa.film_id], actor_key[fa.actor_id])
            if tgt.get(t.BridgeFilmActor, ids) is None:
                tgt.add(t.BridgeFilmActor(film_key=ids[0], actor_key=ids[1]))

        for fc in src.scalars(select(s.FilmCategory).where(s.FilmCategory.last_update >= old["film_category"])).all():
            ids = (film_key[fc.film_id], category_key[fc.category_id])
            if tgt.get(t.BridgeFilmCategory, ids) is None:
                tgt.add(t.BridgeFilmCategory(film_key=ids[0], category_key=ids[1]))

        # ---- facts ----
        rentals = src.execute(
            select(s.Rental, s.Inventory)
            .join(s.Inventory, s.Inventory.inventory_id == s.Rental.inventory_id)
            .where(s.Rental.last_update >= old["rental"])).all()
        for r, inv in rentals:
            add_date(tgt, r.rental_date.date())
            returned = None
            days = None
            if r.return_date:
                add_date(tgt, r.return_date.date())
                returned = date_key(r.return_date)
                days = (r.return_date.date() - r.rental_date.date()).days
            save(tgt, t.FactRental, "rental_id", dict(
                rental_id=r.rental_id, date_key_rented=date_key(r.rental_date),
                date_key_returned=returned, film_key=film_key[inv.film_id],
                store_key=store_key[inv.store_id],
                customer_key=customer_key[r.customer_id],
                staff_id=r.staff_id, rental_duration_days=days))

        for p in src.scalars(select(s.Payment).where(s.Payment.last_update >= old["payment"])).all():
            if p.rental_id:
                rental = src.get(s.Rental, p.rental_id)
                store_id = src.get(s.Inventory, rental.inventory_id).store_id
            else:
                store_id = src.get(s.Staff, p.staff_id).store_id
            add_date(tgt, p.payment_date.date())
            save(tgt, t.FactPayment, "payment_id", dict(
                payment_id=p.payment_id, date_key_paid=date_key(p.payment_date),
                customer_key=customer_key[p.customer_id],
                store_key=store_key[store_id], staff_id=p.staff_id,
                amount=p.amount))

        # ---- save the new markers ----
        for name, model in MODELS.items():
            newest = src.scalar(select(func.max(model.last_update))) or old[name]
            state = tgt.get(t.SyncState, name)
            if state is None:
                tgt.add(t.SyncState(table_name=name, last_update=newest))
            else:
                state.last_update = newest

    log.info("sync done: %s rentals read", len(rentals))
