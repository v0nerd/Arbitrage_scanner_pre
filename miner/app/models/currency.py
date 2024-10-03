from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    PrimaryKeyConstraint,
    UniqueConstraint,
)
from app.db.base_class import Base


class Currency(Base):
    __tablename__ = "currency"

    id = Column(Integer, primary_key=True)
    pair = Column(String(256), nullable=False)
    exchange_from = Column(String(256), nullable=False)
    exchange_to = Column(String(256), nullable=False)
    price_from = Column(Float, nullable=False)
    price_to = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    time_from = Column(String(256), nullable=False)
    profit = Column(Float, nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "pair", "exchange_from", "exchange_to", name="unique_currency_constraint"
        ),
    )
