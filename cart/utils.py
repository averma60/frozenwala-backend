import requests


def item_stock_quantity(item_id):
    """Get avaialble stock quantity for specific item"""
    stock_quantity = 0
    try:
        response = requests.get(f'https://bills.megasgoods.com/api/stocks?limit=10000&id={item_id}')
        if response.status_code == 200:
            json_data = response.json()
            stock_data = json_data.get('data', {})
            stock_quantity = int(float(stock_data.get('available_qty', 0)))
    except Exception as e:
        pass

    return stock_quantity
