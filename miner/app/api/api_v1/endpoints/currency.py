from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Any, Optional

from app import crud
from app.api import deps
from app.schemas.currency import Currency, CurrencyCreate, CurrencyUpdate

router = APIRouter()


@router.get("/{currency_id}", status_code=200, response_model=Currency)
def fetch_currency(
    *,
    currency_id: int,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Fetch a single currency by ID
    """
    result = crud.currency.get(db=db, id=currency_id)
    if not result:
        # the exception is raised, not returned - you will get a validation
        # error otherwise.
        raise HTTPException(
            status_code=404, detail=f"Currency with ID {currency_id} not found"
        )

    return result

@router.post("/", status_code=201, response_model=Currency)
def create_currency(
    *, currency_in: CurrencyCreate, db: Session = Depends(deps.get_db)
) -> dict:
    """
    Create a new currency in the database.
    """
    currency = crud.currency.create(db=db, obj_in=currency_in)

    return currency
