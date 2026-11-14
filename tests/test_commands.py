from datetime import datetime

from sqlalchemy import func, select

from config import SourceSession, TargetSession
from conftest import run
import models_source as s
import models_target as t


def test_init():
    assert run("init") == 0


def test_full_load():
    run("init")
    run("full-load")
    with SourceSession() as src, TargetSession() as tgt:
        a = src.scalar(select(func.count()).select_from(s.Rental))
        b = tgt.scalar(select(func.count()).select_from(t.FactRental))
        assert a == b


def test_incremental_new():
    run("init")
    run("full-load")
    with SourceSession.begin() as src:
        new = s.Rental(rental_date=datetime(2006, 3, 1), inventory_id=1,
                       customer_id=1, staff_id=1, last_update=datetime.now())
        src.add(new)
        src.flush()
        rental_id = new.rental_id
    run("incremental")
    with TargetSession() as tgt:
        row = tgt.scalar(select(t.FactRental).where(t.FactRental.rental_id == rental_id))
        assert row is not None
    with SourceSession.begin() as src:
        src.delete(src.get(s.Rental, rental_id))


def test_incremental_updates():
    run("init")
    run("full-load")
    with TargetSession() as tgt:
        old_city = tgt.scalar(select(t.DimCustomer.city).where(t.DimCustomer.customer_id == 1))
    with SourceSession.begin() as src:
        src.get(s.Rental, 11496).return_date = datetime(2006, 2, 15)
        src.get(s.Customer, 1).address_id = 6
    run("incremental")
    with TargetSession() as tgt:
        fact = tgt.scalar(select(t.FactRental).where(t.FactRental.rental_id == 11496))
        city = tgt.scalar(select(t.DimCustomer.city).where(t.DimCustomer.customer_id == 1))
        assert fact.date_key_returned == 20060215
        assert city != old_city
    with SourceSession.begin() as src:
        src.get(s.Rental, 11496).return_date = None
        src.get(s.Customer, 1).address_id = 5


def test_validate():
    run("init")
    run("full-load")
    assert run("validate") == 0
    with TargetSession.begin() as tgt:
        latest = select(t.FactPayment).order_by(t.FactPayment.date_key_paid.desc())
        tgt.delete(tgt.scalars(latest).first())
    assert run("validate") == 1
