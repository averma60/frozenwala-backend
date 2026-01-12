# consumers.py
import json
from channels.generic.websocket import WebsocketConsumer
from .models import Order

class PendingOrdersConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    def fetch_pending_orders_count(self, event):
        pending_orders_count = Order.objects.filter(status='1').count()
        self.send(text_data=json.dumps({'pending_orders_count': pending_orders_count}))
