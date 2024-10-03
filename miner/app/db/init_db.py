import logging
import asyncio
from sqlalchemy.orm import Session

from app import crud, schemas
from app.db import base  # noqa: F401
from app.core.config import settings
from app.Coinpaprika import get_usdt_pairs
from app.utils import usdt_pairs

logger = logging.getLogger(__name__)


# make sure all SQL Alchemy models are imported (app.db.base) before initializing DB
# otherwise, SQL Alchemy might fail to initialize relationships properly
# for more details: https://github.com/tiangolo/full-stack-fastapi-postgresql/issues/28


def init_db(db: Session) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next line
    # Base.metadata.create_all(bind=engine)

    # currency = crud.currency.get_by_pair_exchange(db, pair="BTC/USD")

    db_pairs = usdt_pairs()

    if db_pairs:
        print(len(db_pairs), "are inserted to DB")
        for pair_gruop in db_pairs:
            currency_in = schemas.CurrencyCreate(
                pair=pair_gruop["pair"],
                exchange_from=pair_gruop["exchange_from"],
                exchange_to=pair_gruop["exchange_to"],
                price_from=pair_gruop["price_from"],
                price_to=pair_gruop["price_to"],
                volume=pair_gruop["volume"],
                profit=pair_gruop["profit"],
                time_from=(pair_gruop["time_from"]).strftime("%Y-%m-%d %H:%M:%S"),
            )
            crud.currency.create(db, obj_in=currency_in)
