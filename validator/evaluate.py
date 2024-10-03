import time
from typing import List, Dict, Any
import requests

from get_from_server import get_common_usdt_pairs, get_from_rapidapi


# Define a basic Miner class
class Miner:
    def __init__(
        self,
        miner_id: str,
        miner_data_url: str = "http://localhost:8001/get-values",
        miner_update_url: str = "http://localhost:8001/update-status",
    ):
        self.miner_id = miner_id
        # self.miner_url = f"http://localhost:8001/miner/{miner_id}"
        self.miner_url = miner_data_url
        self.miner_update_url = miner_update_url

    # def scan_arbitrage(self) -> List[Dict[str, Any]]:
    #     # Placeholder for actual arbitrage scanning logic
    #     # Simulate scanning time
    #     time.sleep(1)
    #     return [
    #         {"pair": "BTC/USDT", "profit": 100, "timestamp": time.time()},
    #         {"pair": "ETH/USDT", "profit": 150, "timestamp": time.time()},
    #     ]

    def get_scanner_data(self):

        url = self.miner_url

        response = requests.get(url)

        if response.status_code == 200:
            print("Successfully connected to the miner")
            return (response.json())["data"]

        else:
            # print("Error: ", response.status_code)
            return None


# A function to check the update frequency of a miner every 30 seconds and return the time interval
def check_update_frequency(miner_update_url, interval_seconds=30, iterations=20):
    # url = f"http://localhost:8001/update-status"
    url = miner_update_url
    last_timestamp = None

    for _ in range(iterations):
        response = requests.get(url)
        data = response.json()
        current_timestamp = data.get("last_updated")
        print(f"Update at {current_timestamp}")

        if last_timestamp and current_timestamp != last_timestamp:
            print(f"Data updated. Time interval: {interval_seconds} seconds")
            return current_timestamp - last_timestamp

        last_timestamp = current_timestamp
        time.sleep(interval_seconds)
    else:  # This block will execute if the loop completes without a break
        print("No updates detected within the specified time interval.")
        return None


# Function to normalize values (assuming all values are positive and non-zero)
def normalize(value, min_value, max_value):
    return (value - min_value) / (max_value - min_value)


# Validator class to check miner performance
class Validator:
    def __init__(self):
        self.performance_data = {}

    def evaluate_results(self, miner: Miner) -> dict:
        # Example evaluation criteria: count valid opportunities based on profit

        matching_pairs = []

        miner_data_all = miner.get_scanner_data()
        end_time = time.time()

        val_data_all = get_common_usdt_pairs()
        # val_data_all = get_from_rapidapi()
        print(len(val_data_all))

        for val_data in val_data_all:
            for miner_data in miner_data_all:

                # When we use coinpaprika api
                if (
                    val_data["pair"] == miner_data["pair"]
                    and val_data["exchange_to"] == miner_data["exchange_to"]
                    and val_data["exchange_from"] == miner_data["exchange_from"]
                ):
                    matching_pairs.append((val_data, miner_data))

                # When we use rapidapi api
                # if (
                #     val_data["coin"] == miner_data["pair"]
                #     and val_data["buyAt"] == miner_data["exchange_to"]
                #     and val_data["sellAt"] == miner_data["exchange_from"]
                # ):
                #     matching_pairs.append((val_data, miner_data))

        # Output the matching pairs
        # for match in matching_pairs:
        #     print(f"Match found:\n val_data: {match[0]}\n miner_data: {match[1]}\n")

        # return sum(1 for result in results if result["profit"] > 0)
        return {
            "data_accuracy": 100 * (len(matching_pairs) / len(val_data_all)),
            "end_time": end_time,
        }

    WEIGHTS = {
        "response_time": 0.1,
        "data_accuracy": 0.7,
        "uptime": 0.2,
    }

    def validate_miner(self, miner: Miner) -> None:
        start_time = time.time()

        # # Get the arbitrage opportunities from the miner
        # results = miner.get_scanner_data()

        # Evaluate results (simulated performance check)
        valid_opportunities = self.evaluate_results(miner=miner)

        # Calculate time taken
        elapsed_time = valid_opportunities["end_time"] - start_time

        update_frequency = check_update_frequency(miner.miner_update_url)

        # Store performance data
        self.performance_data[miner.miner_id] = {
            "data_accuracy": valid_opportunities["data_accuracy"],
            "elapsed_time": elapsed_time,
        }

        # Normalization of values based on assumed ranges
        normalized_response_time = 1 - normalize(
            elapsed_time, 0, 2
        )  # Inverse for lower is better
        normalized_data_accuracy = normalize(
            valid_opportunities["data_accuracy"], 0, 100
        )
        normalized_uptime = 1 - normalize((update_frequency / 600), 0, 1)

        # Weighted score calculation
        total_score = (
            normalized_response_time * self.WEIGHTS["response_time"]
            + normalized_data_accuracy * self.WEIGHTS["data_accuracy"]
            + normalized_uptime * self.WEIGHTS["uptime"]
        )

        return {
            "miner_id": miner.miner_id,
            "data_accuracy": valid_opportunities["data_accuracy"],
            "update_frequency": str(update_frequency) + "seconds",
            "elapsed_time": elapsed_time,
            "total_score": total_score,
        }


# Example usage
if __name__ == "__main__":
    miner1 = Miner("Miner_1")
    miner2 = Miner("Miner_2")

    validator = Validator()

    # Validate multiple miners
    # validator.validate_miner(miner1)
    # validator.validate_miner(miner2)

    # Print performance metrics
    print(validator.validate_miner(miner1))


# listA = [
#     {
#         "coin": "BTC",
#         "buyAt": "Exchange1",
#         "sellAt": "Exchange2",
#         "sellPrice": 10000,
#         "buyPrice": 9500,
#         "profit": 500,
#     },
#     {
#         "coin": "ETH",
#         "buyAt": "Exchange3",
#         "sellAt": "Exchange4",
#         "sellPrice": 500,
#         "buyPrice": 450,
#         "profit": 50,
#     },
#     # Add more objects as needed
# ]

# listB = [
#     {
#         "pair": "BTC",
#         "exchange_from": "Exchange1",
#         "exchange_to": "Exchange2",
#         "volume": 1.5,
#         "price_from": 9500,
#         "price_to": 10000,
#         "profit": 500,
#         "time_from": "2024-08-22 11:00:00",
#     },
#     {
#         "pair": "ETH",
#         "exchange_from": "Exchange3",
#         "exchange_to": "Exchange4",
#         "volume": 2.0,
#         "price_from": 450,
#         "price_to": 500,
#         "profit": 50,
#         "time_from": "2024-08-22 12:00:00",
#     },
#     # Add more objects as needed
# ]
