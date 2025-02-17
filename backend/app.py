from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from datetime import datetime

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})


class TransactionAggregator:
    def __init__(self, transactions):
        
        """
        Initialize TransactionAggregator with a list of transactions.

        :param transactions: List of transactions in the following format:
            {
                "transaction_id": str,
                "customer_id": str,
                "date": str,
                "items": [
                    {
                        "item_id": str,
                        "name": str,
                        "price": float,
                        "quantity": int
                    }
                ],
                "total_amount": float
            }
        """
        self.transactions = transactions

    def filter_transactions(self, filters):
        
        """
        Filter transactions based on a given set of filters.

        Supported filters are 'customer_id', 'item_id', and 'date_range'.
        'date_range' should be a dictionary with keys 'start' and 'end' in the format
        '%Y-%m-%d'.

        :param filters: a dictionary of filters
        :return: a list of transactions that match the filters
        """
        filtered = self.transactions

        if "customer_id" in filters:
            filtered = [
                t for t in filtered if t["customer_id"] == int(filters["customer_id"])
            ]

        if "item_id" in filters:
            target_id = int(filters["item_id"])
            result = []
            for transaction in filtered:
                for item in transaction["items"]:
                    if item["item_id"] == target_id:
                        result.append(transaction)
                        break
            filtered = result

        if "date_range" in filters:
            start = datetime.strptime(filters["date_range"]["start"], "%Y-%m-%d")
            end = datetime.strptime(filters["date_range"]["end"], "%Y-%m-%d")
            filtered = [
                t
                for t in filtered
                if start <= datetime.strptime(t["date"], "%Y-%m-%d") <= end
            ]

        return filtered

    def aggregate_by(self, group_by, filtered_transactions):
        """
        Aggregate a list of transactions based on a given group_by field.

        :param group_by: either 'customer_id', 'item_id', or 'date'
        :param filtered_transactions: a list of transactions
        :return: a list of dictionaries, each containing aggregated values for a
            group of transactions
        """
        if group_by == "customer_id":
            return self.aggregate_by_customer(filtered_transactions)
        elif group_by == "item_id":
            return self.aggregate_by_item(filtered_transactions)
        elif group_by == "date":
            return self.aggregate_by_date(filtered_transactions)
        return filtered_transactions

    def aggregate_by_customer(self, transactions):
        """
        Aggregate transactions by customer_id, returning a list of dictionaries
        containing customer_id and total_revenue for each customer.

        :param transactions: a list of transactions
        :return: a list of dictionaries with total revenue for each customer
        """
        result = {}
        for t in transactions:
            cid = t["customer_id"]
            if cid not in result:
                result[cid] = {"customer_id": cid, "total_revenue": 0}
            result[cid]["total_revenue"] += t["total_amount"]
        return list(result.values())

    def aggregate_by_item(self, transactions):
        """
        Aggregate transactions by item_id, returning a list of dictionaries
        containing item_id, name and total_quantity for each item.

        :param transactions: a list of transactions
        :return: a list of dictionaries with total quantity for each item
        """
        result = {}
        for t in transactions:
            for item in t["items"]:
                iid = item["item_id"]
                if iid not in result:
                    result[iid] = {
                        "item_id": iid,
                        "name": item["name"],
                        "total_quantity": 0,
                    }
                result[iid]["total_quantity"] += item["quantity"]
        return list(result.values())

    def aggregate_by_date(self, transactions):
        """
        Aggregate transactions by date, returning a list of dictionaries
        containing date and total_revenue for each date.

        :param transactions: a list of transactions
        :return: a list of dictionaries with total revenue for each date
        """
        result = {}
        for t in transactions:
            date = t["date"]
            if date not in result:
                result[date] = {"date": date, "total_revenue": 0}
            result[date]["total_revenue"] += t["total_amount"]
        return list(result.values())


@app.route("/", methods=["POST"])
def transactions_list():
    with open("data.json") as f:
        data = json.load(f)
    aggregator = TransactionAggregator(data)

    request_data = request.get_json() or {}
    filters = {}

    if "customer_id" in request_data:
        filters["customer_id"] = request_data["customer_id"]
    if "item_id" in request_data:
        filters["item_id"] = request_data["item_id"]
    if "date_range" in request_data:
        filters["date_range"] = request_data["date_range"]

    filtered_data = aggregator.filter_transactions(filters)

    group_by = request_data.get("group_by")
    if group_by:
        result = aggregator.aggregate_by(group_by, filtered_data)
    else:
        result = filtered_data

    return jsonify(result)





if __name__ == "__main__":
    app.run(debug=True)
