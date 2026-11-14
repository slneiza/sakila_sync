import os
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker

source_engine = create_engine(URL.create(
    "mysql+pymysql",
    username=os.environ["MYSQL_USER"],
    password=os.environ["MYSQL_PASSWORD"],
    host=os.environ.get("MYSQL_HOST", "127.0.0.1"),
    port=int(os.environ.get("MYSQL_PORT", "3306")),
    database=os.environ["MYSQL_DATABASE"],
))
target_engine = create_engine(f"sqlite:///{os.environ.get('SQLITE_PATH', 'analytics.db')}")

SourceSession = sessionmaker(source_engine)
TargetSession = sessionmaker(target_engine)
