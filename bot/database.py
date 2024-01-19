from dotenv import dotenv_values
from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    Integer,
    Sequence,
    SmallInteger,
    create_engine,
)
from sqlalchemy.engine import URL
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

env = dotenv_values('../.env')
HOST = env.get('HOST')
DATABASE = env.get('DATABASE')
USERNAME = env.get('USERNAME')
PASSWORD = env.get('PASSWORD')

url = URL.create(
    drivername='postgresql',
    host=HOST,
    database=DATABASE,
    username=USERNAME,
    password=PASSWORD,
)

engine = create_engine(url, client_encoding='utf8')

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(BigInteger, primary_key=True)
    in_game = Column(Boolean, default=False)
    secret_num = Column(SmallInteger, default=None)
    attempts = Column(Integer, default=None)
    total_games = Column(Integer, default=0)
    wins = Column(Integer, default=0)


Session = sessionmaker(bind=engine)

if __name__ == '__main__':
    Base.metadata.create_all(engine)
