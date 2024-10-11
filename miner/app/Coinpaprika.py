import requests
from datetime import datetime, timedelta


def get_usdt_pairs():
    # Get exchanges data from CoinPaprika
    exchanges_url = "https://api.coinpaprika.com/v1/exchanges"
    # exchanges_url1 = "https://api.coingecko.com/api/v3"
    exchanges_response = requests.get(exchanges_url, timeout=60)

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
        # Get markets for the 15 exchange
        if count > 20:
            break

        count += 1

        if count > 0:

            markets_url = (
                f"https://api.coinpaprika.com/v1/exchanges/{exchange['id']}/markets"
            )
            markets_response = requests.get(markets_url, timeout=60)

            if markets_response.status_code != 200:
                print(f"Error fetching markets for {exchange['name']}")
                continue

            markets = markets_response.json()

            # Filter for pairs that include USDT
            for market in markets:
                # Check if the market contains USDT and the last_updated is within the last 10 minutes
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
                    # print(
                    #     (
                    #         datetime.now()
                    #         - datetime.fromisoformat(market["last_updated"][:-1])
                    #         + timedelta(hours=4)
                    #     ).total_seconds()
                    # )
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


# Get all currency/USDT pairs
usdt_pairs = get_usdt_pairs()

# Print the results
# for pair in usdt_pairs:
#     print(
#         f"Exchange: {pair['exchange']}, Pair: {pair['pair']}, "
#         f"Price: {pair['price']}, Volume: {pair['volume']}, "
#         f"Last Updated: {pair['timestamp']}"
#     )
