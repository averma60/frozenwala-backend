import requests
import logging

logger = logging.getLogger("debug_logs")

def update_stock(item_id, quantity):
    """
    Update stock information by making a POST request to the external API.
    """
    try:
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

        logger.info(
            f"Stock Updated | Item: {item_id} | Qty: {quantity} | Status: {response.status_code} | Response: {response.text}"
        )

        return response.status_code, response.text
    except Exception as e:
        logger.error(
            f"Stock Update Failed | Item: {item_id} | Qty: {quantity} | Error: {str(e)}"
        )

def sale_sync(order, user_id, items):
    """Sync sale with billing software"""
    try:
        url = "https://bills.megasgoods.com/api/order/sync-to-sales"

        headers = {
            "Content-Type": "application/json",
        }

        payload = {
            "order_id": order.id + 1000,
            "store_id": 1,
            "warehouse_id": 2,
            "customer_id": user_id,
            "order_date": order.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "payment_status": "PAID",
            "sales_status": "Completed" if order.status == "4" else "Pending",
            "subtotal": order.total_price,
            "grand_total": order.total_price,
            "items": items
        }

        response = requests.post(url, json=payload, headers=headers)

        logger.info(
            f"Sale Sync | Order: #{order.id + 1000} | User: {user_id} | "
            f"Status: {response.status_code} | Response: {response.text}"
        )
        return response.status_code, response.text
    except Exception as e:
        logger.error(
            f"Sale Sync Failed | Order: #{order.id + 1000} | "
            f"User: {user_id} | Error: {str(e)}"
        )
