import os
os.environ["MYSQL_DATABASE"] = "sakila_test"   # never touch the real sakila
os.environ["SQLITE_PATH"] = "test_analytics.db"

import sys

import pytest

import cli
from config import target_engine
from models_target import TargetBase


@pytest.fixture(autouse=True)
def fresh_sqlite():
    TargetBase.metadata.drop_all(target_engine)


def run(*args):
    sys.argv = ["cli.py", *args]
    return cli.main()
