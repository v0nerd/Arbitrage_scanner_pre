import time
import asyncio

from pathlib import Path

from fastapi import FastAPI, APIRouter, Depends
from fastapi.templating import Jinja2Templates

# from fastapi import Request
from sqlalchemy.orm import Session
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from fastapi.responses import HTMLResponse
from starlette.requests import Request
from datetime import datetime, timedelta
import pytz

from app import crud
from app.api import deps
from app.api.api_v1.api import api_router
from app.core.config import settings
from app.utils import update_records

from app.db.session import SessionLocal
from app.schemas.currency import Currency


BASE_PATH = Path(__file__).resolve().parent

root_router = APIRouter()
app = FastAPI(title="Miner_Get_Arbitrage_Data")

TEMPLATES = Jinja2Templates(directory=str(BASE_PATH / "templates"))

runnig = False
update_timers = time.time()

@root_router.get("/", status_code=200)
async def root(
    request: Request,
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    Root GET
    """
    data = await crud.currency.get_data(db=db)

    now = datetime.now()

    for item in data:
        # Convert item.time_from to datetime
        time_from = datetime.fromisoformat(item.time_from)  # Adjust format as needed
        elapsed_time = now - time_from + timedelta(hours=4)

        total_seconds = int(elapsed_time.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        formatted_elapsed_time = f"{hours:02}h {minutes:02}m {seconds:02}s"
        item.elapsed_time = formatted_elapsed_time

    return TEMPLATES.TemplateResponse("table.html", {"request": request, "data": data})

    # return {"message": "Welcome to this fantastic app."}


db = SessionLocal()
app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(root_router)


# Update the arbitrage data every ten minutes
# async def update_run():
#     while True:
#         await update_records(db=db)
#         print("Records updated. Waiting 1 minute for the next update.")
#         await asyncio.sleep(60)  # Use asyncio.sleep instead of time.sleep

# Scheduler setup
scheduler = AsyncIOScheduler()


async def update_run():
    # global runnig
    # while runnig:
    global update_timers
    update_timers = time.time()
    await update_records(db=db)
    print("Records updated. Waiting 7 minute for the next update.")
    # await asyncio.sleep(180)  # Use asyncio.sleep instead of time.sleep


# @app.on_event("startup")
# async def startup_event():
#     global running
#     running = True  # Set running to True when the application starts
#     print("Starting the update task...")
#     asyncio.create_task(update_run())  # Start the background task


@app.on_event("startup")
async def startup_event():
    print("Starting the update task...")
    scheduler.add_job(
        update_run, IntervalTrigger(minutes=7)
    )  # Schedule to run every 7 minute
    scheduler.start()


@app.on_event("shutdown")
async def shutdown_event():
    # global runnig
    # runnig = False  # Stop the background task when shutting down
    print("Application shut down")
    scheduler.shutdown()


# @app.post("/stop-update")
# async def stop_update():
#     global runnig
#     runnig = False
#     return {"message": "Update stopped"}


# Endpoint to trigger an update automatically after responding
@app.get("/get-values", status_code=200)
async def fetch_values():
    global update_timers
    try:

        data = await crud.currency.get_data(
            db=db
        )  # Replace with your actual data retrieval function

        return {"message": "Data fetched", "data": data}

    except Exception as e:
        print(e)
        raise e
    
@app.get("/update-status", status_code=200)
async def fetch_values():
    global update_timers
    return {"message": "Data fetched", "last_updated": update_timers}
    

# @app.post("/get-values", status_code=200)
# async def fetch_values(input_num: int = 1):
#     if input_num:
#         await stop_update()
#         global runnig
#         if not runnig:

#             data = await crud.currency.get_data(
#                 db=db
#             )  # Replace with your actual data retrieval function

#             runnig = True
#             asyncio.create_task(update_run())
#             return {"message": "Update started", "data": data}
#         else:
#             return {"message": "Update is already running"}


if __name__ == "__main__":
    # Use this for debugging purposes only
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="debug")
