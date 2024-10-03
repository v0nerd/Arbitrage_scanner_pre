import requests
from datetime import datetime


def get_usdt_pairs():
    # Get exchanges data from CoinPaprika
    exchanges_url = "https://api.coinpaprika.com/v1/exchanges"
    exchanges_response = requests.get(exchanges_url)

    if exchanges_response.status_code != 200:
        print("Error fetching exchanges data")
        return

    exchanges = exchanges_response.json()

    usdt_pairs = []

    count = 0
    # Iterate through each exchange to get its markets
    for exchange in exchanges:
        """Giving limitation to 60 requests per hour"""

        count += 1

        if count > 20:
            break

        if count > 5:
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
                if "/USDT" in market["pair"]:
                    # Extract relevant data from the market information directly
                    usdt_pairs.append(
                        {
                            "exchange": exchange["name"],
                            "pair": market["pair"],
                            "price": market["quotes"]["USD"][
                                "price"
                            ],  # Adjust based on available fields
                            "volume": market["quotes"]["USD"][
                                "volume_24h"
                            ],  # Adjust based on available fields
                            "timestamp": datetime.fromisoformat(
                                market["last_updated"][:-1]
                            ),  # Convert to datetime
                        }
                    )

    return usdt_pairs

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
                if ex1["exchange"] != ex2["exchange"] and ex1["price"] != ex2["price"]:
                    item = {
                        "pair": pair,
                        "exchange_from": ex1["exchange"] if ex1["price"] < ex2["price"] else ex2["exchange"],
                        "exchange_to": ex2["exchange"] if ex1["price"] < ex2["price"] else ex1["exchange"],
                        "price_from": min(ex1["price"], ex2["price"]),
                        "price_to": max(ex1["price"], ex2["price"]),
                        "volume": ex1["volume"] if ex1["price"] > ex2["price"] else ex2["volume"],
                        "profit": (
                            100 * (min(ex1["price"], ex2["price"]) / max(ex1["price"], ex2["price"])) - 100
                        ),
                        "time_from": max(ex1["timestamp"], ex2["timestamp"]),
                    }
                    db_pairs.append(item)

    return db_pairs

print(usdt_pairs())