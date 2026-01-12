# websocket_app/routing.py
from django.urls import path
from .consumers import PendingOrdersConsumer

websocket_urlpatterns = [
    path('ws/pending-orders/', PendingOrdersConsumer.as_asgi()),
]
