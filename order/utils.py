import requests

def update_stock(item_id, quantity):
    """
    Update stock information by making a POST request to the external API.
    """
    url = "https://bills.megasgoods.com/api/stock_sync/update_stock"

    headers = {
        "Content-Type": "application/json",
    }

    payload = {
        "item_id": item_id,
        "quantity": quantity,
        "piece_qty": quantity
    }

    response = requests.post(url, json=payload, headers=headers)

    return response.status_code, response.text
