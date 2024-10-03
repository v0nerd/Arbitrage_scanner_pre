pip install -r requirements.txt
export PYTHONPATH=.
alembic revision --autogenerate -m "MINER_RESULT_TABLE"

bash ./prestart.sh
bash ./run.sh
