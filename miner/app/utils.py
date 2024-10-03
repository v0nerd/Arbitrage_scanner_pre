from fastapi import Depends
import asyncio

from app.Coinpaprika import get_usdt_pairs

from app.schemas.currency import (
    CurrencyCreate,
    CurrencyUpdate,
)
from app import crud
from app.api import deps

from app.db.session import SessionLocal
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession


# def usdt_pairs():

#     Currency_data = get_usdt_pairs()

#     # Get the data from the Coinpaprika API for DB
#     db_pairs = []
#     if Currency_data == None:
#         return None

#     for pointer in range(0, len(Currency_data)):
#         if Currency_data[pointer]["volume"] != 0:
#             for pointer2 in range(pointer + 1, len(Currency_data)):
#                 if (
#                     Currency_data[pointer]["exchange"]
#                     != Currency_data[pointer2]["exchange"]
#                     and Currency_data[pointer2]["volume"] != 0
#                     and Currency_data[pointer]["price"]
#                     != Currency_data[pointer2]["price"]
#                 ):
#                     if (
#                         Currency_data[pointer]["pair"]
#                         == Currency_data[pointer2]["pair"]
#                     ):
#                         item = {}
#                         item["pair"] = Currency_data[pointer]["pair"]
#                         item["exchange_from"] = (
#                             Currency_data[pointer]["exchange"]
#                             if Currency_data[pointer]["price"]
#                             < Currency_data[pointer2]["price"]
#                             else Currency_data[pointer2]["exchange"]
#                         )
#                         item["exchange_to"] = (
#                             Currency_data[pointer2]["exchange"]
#                             if Currency_data[pointer]["price"]
#                             < Currency_data[pointer2]["price"]
#                             else Currency_data[pointer]["exchange"]
#                         )
#                         item["price_from"] = (
#                             Currency_data[pointer]["price"]
#                             if Currency_data[pointer]["price"]
#                             < Currency_data[pointer2]["price"]
#                             else Currency_data[pointer2]["price"]
#                         )
#                         item["price_to"] = (
#                             Currency_data[pointer]["price"]
#                             if Currency_data[pointer]["price"]
#                             > Currency_data[pointer2]["price"]
#                             else Currency_data[pointer2]["price"]
#                         )
#                         item["volume"] = (
#                             Currency_data[pointer]["volume"]
#                             if Currency_data[pointer]["price"]
#                             > Currency_data[pointer2]["price"]
#                             else Currency_data[pointer2]["volume"]
#                         )
#                         item["profit"] = (
#                             (
#                                 100
#                                 * (
#                                     Currency_data[pointer]["price"]
#                                     / Currency_data[pointer2]["price"]
#                                 )
#                                 - 100
#                             )
#                             if Currency_data[pointer]["price"]
#                             > Currency_data[pointer2]["price"]
#                             else (
#                                 100
#                                 * (
#                                     Currency_data[pointer2]["price"]
#                                     / Currency_data[pointer]["price"]
#                                 )
#                                 - 100
#                             )
#                         )
#                         item["time_from"] = (
#                             Currency_data[pointer]["timestamp"]
#                             if Currency_data[pointer]["timestamp"]
#                             > Currency_data[pointer2]["timestamp"]
#                             else Currency_data[pointer2]["timestamp"]
#                         )

#                         db_pairs.append(item)
#         # comment:
#     # end for

#     return db_pairs


def usdt_pairs():
    Currency_data = get_usdt_pairs()

    # Check if data is valid
    if Currency_data is None:
        return None

    # Use a dictionary to group exchanges by pair
    pairs_dict = {}
    for data in Currency_data:
        if data["volume"] != 0:
            pair = data["pair"]
            if pair not in pairs_dict:
                pairs_dict[pair] = []
            pairs_dict[pair].append(data)

    db_pairs = []

    # Process pairs in the grouped dictionary
    for pair, exchanges in pairs_dict.items():
        if len(exchanges) < 2:
            continue

        for i in range(len(exchanges)):
            for j in range(i + 1, len(exchanges)):
                ex1 = exchanges[i]
                ex2 = exchanges[j]
                if (
                    ex1["exchange"] != ex2["exchange"]
                    and ex1["price"] != ex2["price"]
                    and ex1["currency_id"] == ex2["currency_id"]
                    and (ex1["outlier"] or ex2["outlier"])
                ):
                    item = {
                        "pair": pair + "(" + ex1["currency_name"] + ")",
                        "exchange_from": (
                            ex1["exchange"]
                            if ex1["price"] < ex2["price"]
                            else ex2["exchange"]
                        ),
                        "exchange_to": (
                            ex2["exchange"]
                            if ex1["price"] < ex2["price"]
                            else ex1["exchange"]
                        ),
                        "price_from": min(ex1["price"], ex2["price"]),
                        "price_to": max(ex1["price"], ex2["price"]),
                        "volume": (
                            ex1["volume"]
                            if ex1["price"] > ex2["price"]
                            else ex2["volume"]
                        ),
                        "profit": (
                            100
                            * (
                                max(ex1["price"], ex2["price"])
                                / min(ex1["price"], ex2["price"])
                            )
                            - 100
                        ),
                        "time_from": max(ex1["timestamp"], ex2["timestamp"]),
                    }
                    db_pairs.append(item)

    return db_pairs


# end def


# Update the records in the DB
async def update_records(db: Session) -> None:
    try:
        db_pairs = usdt_pairs()
        if db_pairs:

            print(len(db_pairs), "are detected.")
            await crud.currency.batch_update(
                db=db,
                update_values=db_pairs,
            )
            db.commit()

        else:
            print("No new data to update")
    except Exception as e:
        print(e)
        db.rollback()
        raise e
    finally:
        db.close()

    return None
