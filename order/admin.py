from django.contrib import admin
from .models import Order, PaymentOption, DeliverySlot


admin.site.register(Order)
admin.site.register(PaymentOption)
admin.site.register(DeliverySlot)
