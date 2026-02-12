import requests


def fetchStocks():
    """Fetch all stocks from billing software"""
    stock_data = []
    try:
        response = requests.get('https://bills.megasgoods.com/api/stocks?limit=10000')
        if response.status_code == 200:
            json_data = response.json()
            stock_data = json_data.get('data', [])
    except:
        pass

    return stock_data
