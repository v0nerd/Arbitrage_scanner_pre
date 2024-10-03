# Arbitrage_testnet

This is a test project to implement the arbitrage strategy for bittensor.
It is divided into mainly two parts: the `validator` and `miner` modules.

In this part, we do not use the `ccxt` library to get the market data. Instead, we use the `get_from_server` to get the arbitrage data from the server.
The main framework is `fastapi` and we used `sqlalchemy` for the database.

This is pre-release version and we will continue to improve the functions for `axon` and `dendrite`.