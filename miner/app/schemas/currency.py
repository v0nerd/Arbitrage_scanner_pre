from pydantic import BaseModel, HttpUrl


class CurrencyBase(BaseModel):
    exchange_from: str
    exchange_to: str
    pair: str
    price_from: float
    price_to: float
    volume: float
    time_from: str
    profit: float


class CurrencyCreate(CurrencyBase):
    exchange_from: str
    exchange_to: str
    pair: str
    price_from: float
    price_to: float
    volume: float
    time_from: str
    profit: float


class CurrencyUpdate(CurrencyBase):
    price_from: float
    price_to: float
    volume: float
    profit: float


# Properties shared by models stored in DB


class CurrencyInDBBase(CurrencyBase):
    id: int

    class Config:
        orm_mode = True


# Properties to return to client


class Currency(CurrencyInDBBase):
    pass


# Properties properties stored in DB


class CurrencyInDB(CurrencyInDBBase):
    pass
