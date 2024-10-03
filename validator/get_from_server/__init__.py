import requests
from datetime import datetime, timedelta
import json
import os


def save_market_pairs_to_file(data, filename="exchanges.json"):
    existing_data = []

    if os.path.exists(filename):
        try:
            with open(filename, "r") as file:
                existing_data = json.load(file)
        except json.JSONDecodeError:
            print(
                f"Warning: {filename} is not valid JSON. Starting with an empty list."
            )

    existing_data.extend(data)

    with open(filename, "w") as file:
        json.dump(existing_data, file, indent=4)

    print(f"Exchange data saved to {filename}")


def get_usdt_pairs():
    # Get exchanges data from CoinPaprika
    exchanges_url = "https://api.coinpaprika.com/v1/exchanges"
    # exchanges_url1 = "https://api.coingecko.com/api/v3"
    exchanges_response = requests.get(exchanges_url)

    if exchanges_response.status_code != 200:
        print("Error fetching exchanges data")
        return

    exchanges = exchanges_response.json()

    # Filter out exchanges that are not active, have no website, or no API
    filtered_exchanges = [
        exchange
        for exchange in exchanges
        if (exchange["reported_rank"] is not None)
        and exchange["active"]
        and exchange["website_status"]
        and exchange["api_status"]
    ]

    sorted_exchanges = sorted(filtered_exchanges, key=lambda x: x["adjusted_rank"])

    usdt_pairs = []

    count = 0
    # Iterate through each exchange to get its markets
    for exchange in sorted_exchanges:
        """Giving limitation to 60 requests per hour"""

        if count > 2:
            break

        count += 1

        if count > 0:
            markets_url = (
                f"https://api.coinpaprika.com/v1/exchanges/{exchange['id']}/markets"
            )
            markets_response = requests.get(markets_url)

            if markets_response.status_code != 200:
                print(f"Error fetching markets for {exchange['name']}")
                continue

            markets = markets_response.json()

            # Filter for pairs that include USDT
            for market in markets:
                if (
                    ("/USDT" in market["pair"])
                    and (
                        (
                            datetime.now()
                            - datetime.fromisoformat(market["last_updated"][:-1])
                            + timedelta(hours=4)
                        ).total_seconds()
                        < 600
                    )
                    and market["market_url"]
                ):
                    # Extract relevant data from the market information directly
                    usdt_pairs.append(
                        {
                            "exchange": exchange["name"],
                            "pair": market["pair"],
                            "currency_name": market["base_currency_name"],
                            "currency_id": market["base_currency_id"],
                            "outlier": market["outlier"],
                            "price": market["quotes"]["USD"][
                                "price"
                            ],  # Adjust based on available fields
                            "volume": market["quotes"]["USD"]["volume_24h"]
                            / market["quotes"]["USD"][
                                "price"
                            ],  # Adjust based on available fields
                            "timestamp": datetime.fromisoformat(
                                market["last_updated"][:-1]
                            ),  # Convert to datetime
                        }
                    )

    return usdt_pairs


def get_common_usdt_pairs():
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


def get_from_rapidapi():
    url = "https://crypto-arbitrage-scanner1.p.rapidapi.com/arbitrage/"

    headers = {
        "X-RapidAPI-KEY": "c68a89742emsh1b9b03ef1247c5ap195cfbjsn640dc299e59f",
        "X-RapidAPI-Host": "crypto-arbitrage-scanner1.p.rapidapi.com",
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        respond_data = response.json()
        print("number of data from rapidapi server", len(respond_data))
        save_market_pairs_to_file(respond_data, "rapidapi_data.json")

        return respond_data

    else:
        print(f"Failed to retrieve data: {response.status_code}")


# print(get_common_usdt_pairs())
# Print the results
# for pair in usdt_pairs:
#     print(
#         f"Exchange: {pair['exchange']}, Pair: {pair['pair']}, "
#         f"Price: {pair['price']}, Volume: {pair['volume']}, "
#         f"Last Updated: {pair['timestamp']}"
#     )
