from datetime import datetime, timedelta

from sqlalchemy import func, select

from config import SourceSession, TargetSession
import models_source as s
import models_target as t


def run_validate(start=None, end=None):
    errors = []
    with SourceSession() as src, TargetSession() as tgt:
        # default is the 30 days ending on the last payment
        if end is None:
            end = src.scalar(select(func.max(s.Payment.payment_date))).date()
        if start is None:
            start = end - timedelta(days=29)
        low = datetime(start.year, start.month, start.day)
        high = datetime(end.year, end.month, end.day) + timedelta(days=1)
        k1 = int(start.strftime("%Y%m%d"))
        k2 = int(end.strftime("%Y%m%d"))
        print("checking", start, "to", end)

        # rentals
        a = src.scalar(select(func.count()).select_from(s.Rental)
                       .where(s.Rental.rental_date >= low, s.Rental.rental_date < high))
        b = tgt.scalar(select(func.count()).select_from(t.FactRental)
                       .where(t.FactRental.date_key_rented.between(k1, k2)))
        print("rentals:", a, b)
        if a != b:
            errors.append("rental counts don't match")

        # payments
        a = src.scalar(select(func.count()).select_from(s.Payment)
                       .where(s.Payment.payment_date >= low, s.Payment.payment_date < high))
        b = tgt.scalar(select(func.count()).select_from(t.FactPayment)
                       .where(t.FactPayment.date_key_paid.between(k1, k2)))
        print("payments:", a, b)
        if a != b:
            errors.append("payment counts don't match")

        # payment total
        a = src.scalar(select(func.sum(s.Payment.amount))
                       .where(s.Payment.payment_date >= low, s.Payment.payment_date < high))
        b = tgt.scalar(select(func.sum(t.FactPayment.amount))
                       .where(t.FactPayment.date_key_paid.between(k1, k2)))
        print("total:", a, b)
        if abs(float(a or 0) - float(b or 0)) > 0.01:
            errors.append("payment totals don't match")

    return errors
