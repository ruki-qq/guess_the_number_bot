from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    Integer,
    SmallInteger,
)
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(BigInteger, primary_key=True)
    in_game = Column(Boolean, default=False)
    secret_num = Column(SmallInteger, default=None)
    attempts = Column(Integer, default=None)
    total_games = Column(Integer, default=0)
    wins = Column(Integer, default=0)
