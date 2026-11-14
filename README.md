# Sakila Analytics Sync

Copies data from the Sakila database in MySQL into an analytics database in SQLite, using SQLAlchemy.

## Versions

- Python 3.13.5
- SQLAlchemy 2.1.8
- PyMySQL 1.2.4
- pytest 9.2.0
- MySQL 8.0 with the Sakila sample database

## Setup

    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt

You also need MySQL with two copies of Sakila: `sakila` and `sakila_test`. The tests use `sakila_test`.

## Environment variables

    export MYSQL_USER=root
    export MYSQL_PASSWORD=your_password
    export MYSQL_HOST=127.0.0.1
    export MYSQL_PORT=3306
    export MYSQL_DATABASE=sakila
    export SQLITE_PATH=analytics.db

## Commands

    python cli.py init
    python cli.py full-load
    python cli.py incremental
    python cli.py validate [--from YYYY-MM-DD] [--to YYYY-MM-DD]

Each command prints a message and exits with 0 if it worked, non-zero if it failed.

## Tests

    python -m pytest -v

The tests run on `sakila_test` and a separate `test_analytics.db`, so the real data isn't touched.

## Indexes

- Unique index on the id from sakila (film_id, customer_id, rental_id and so on). I need this to find a row that's already there and update it instead of adding it twice.
- Index on the date columns in the two fact tables. validate looks things up by date, so this makes it quicker.
- Index on film_key, store_key and customer_key in the fact tables. Makes it quicker to find the film, store or customer for a rental or payment.
