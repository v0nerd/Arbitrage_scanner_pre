from app.crud.base import CRUDBase
from app.models.currency import Currency

from typing import Any, Dict, Optional, Union, List

from sqlalchemy.orm import Session
from sqlalchemy import update, delete, tuple_
from app.schemas.currency import CurrencyCreate, CurrencyUpdate
import asyncio
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import text


class CRUDCurrency(CRUDBase[Currency, CurrencyCreate, CurrencyUpdate]):
    async def get_by_pair_exchange(
        self, db: Session, *, pair: str, exchage_from: str, exchange_to: str
    ) -> Optional[Currency]:
        return (
            db.query(Currency)
            .filter(
                Currency.pair.lower() == pair.lower(),
                Currency.exchange_from.lower() == exchage_from.lower(),
                Currency.exchange_to.lower() == exchange_to.lower(),
            )
            .first()
        )

    async def get_data(self, db: Session):
        result = db.query(Currency).all()
        return result

    def update(
        self,
        db: Session,
        *,
        db_obj: Currency,
        obj_in: Union[CurrencyUpdate, Dict[str, Any]],
    ) -> Currency:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)

        return super().update(db, db_obj=db_obj, obj_in=update_data)

    # async def batch_update(
    #     self, db: Session, *, update_values: List[Dict[str, Any]], batch_size: int = 100
    # ) -> None:
    #     """
    #     Batch update multiple Currency records or insert them if they do not exist.

    #     :param db: SQLAlchemy Session object.
    #     :param update_values: List of dictionaries where each dictionary contains
    #                         the values to be updated and the keys to identify the record.
    #                         Example: [{"pair": "BTC/USD", "exchange_from": "Binance", "exchange_to": "Coinbase", "price_from": 50000, "price_to": 51000}, ...]
    #     :param batch_size: Number of records to update in each batch.
    #     """
    #     try:

    #         # Get all current records in the database

    #         db.execute(text("PRAGMA journal_mode=WAL;"))

    #         update_identifiers = set(
    #             (record["pair"], record["exchange_from"], record["exchange_to"])
    #             for record in update_values
    #         )

    #         existing_ids = set(
    #             db.query(
    #                 Currency.pair, Currency.exchange_from, Currency.exchange_to
    #             ).all()
    #         )

    #         # Delete records not in update_values
    #         delete_ids = existing_ids - update_identifiers
    #         if delete_ids:
    #             db.query(Currency).filter(
    #                 tuple_(
    #                     Currency.pair, Currency.exchange_from, Currency.exchange_to
    #                 ).in_(delete_ids)
    #             ).delete(synchronize_session=False)
    #             db.commit()

    #         # Proceed with the batch update/insert process
    #         for i in range(0, len(update_values), batch_size):
    #             batch = update_values[i : i + batch_size]

    #             for record in batch:
    #                 stmt = (
    #                     update(Currency)
    #                     .where(
    #                         Currency.pair == record["pair"],
    #                         Currency.exchange_from == record["exchange_from"],
    #                         Currency.exchange_to == record["exchange_to"],
    #                     )
    #                     .values(
    #                         price_from=record.get("price_from"),
    #                         price_to=record.get("price_to"),
    #                         volume=record.get("volume"),
    #                         profit=record.get("profit"),
    #                         # Add other fields as necessary
    #                     )
    #                 )

    #                 # Execute the update statement
    #                 result = db.execute(stmt)

    #                 # print(f"Updated {result.rowcount} rows")

    #                 # Check if any rows were updated
    #                 if result.rowcount == 0:
    #                     # No rows updated, insert the new record
    #                     new_record = Currency(
    #                         pair=record["pair"],
    #                         exchange_from=record["exchange_from"],
    #                         exchange_to=record["exchange_to"],
    #                         price_from=record.get("price_from"),
    #                         price_to=record.get("price_to"),
    #                         volume=record.get("volume"),
    #                         profit=record.get("profit"),
    #                         time_from=(record.get("time_from")).strftime(
    #                             "%Y-%m-%d %H:%M:%S"
    #                         ),
    #                     )
    #                     # print("Inserting new record:", new_record)
    #                     db.add(new_record)

    #             db.commit()
    #     except Exception as e:
    #         db.rollback()
    #         raise e

    async def batch_update(
        self, db: Session, *, update_values: List[Dict[str, Any]], batch_size: int = 100
    ) -> None:
        try:
            # Get all current records in the database
            db.execute(text("PRAGMA journal_mode=WAL;"))

            update_identifiers = set(
                (record["pair"], record["exchange_from"], record["exchange_to"])
                for record in update_values
            )

            existing_ids = set(
                db.query(
                    Currency.pair, Currency.exchange_from, Currency.exchange_to
                ).all()
            )

            # Delete records not in update_values
            delete_ids = existing_ids - update_identifiers
            if delete_ids:
                db.query(Currency).filter(
                    tuple_(
                        Currency.pair, Currency.exchange_from, Currency.exchange_to
                    ).in_(delete_ids)
                ).delete(synchronize_session=False)
                db.commit()

            # Proceed with the batch update/insert process
            for i in range(0, len(update_values), batch_size):
                batch = update_values[i : i + batch_size]

                for record in batch:
                    stmt = (
                        insert(Currency)
                        .values(
                            pair=record["pair"],
                            exchange_from=record["exchange_from"],
                            exchange_to=record["exchange_to"],
                            price_from=record.get("price_from"),
                            price_to=record.get("price_to"),
                            volume=record.get("volume"),
                            profit=record.get("profit"),
                            time_from=(record.get("time_from")).strftime(
                                "%Y-%m-%d %H:%M:%S"
                            ),
                        )
                        .on_conflict_do_update(
                            index_elements=["pair", "exchange_from", "exchange_to"],
                            set_={
                                "price_from": record.get("price_from"),
                                "price_to": record.get("price_to"),
                                "volume": record.get("volume"),
                                "profit": record.get("profit"),
                                # Update other fields as necessary
                            },
                        )
                    )

                    # Execute the UPSERT statement
                    db.execute(stmt)

                db.commit()

        except Exception as e:
            db.rollback()
            raise e


currency = CRUDCurrency(Currency)
