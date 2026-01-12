from django.contrib import admin
from .models import Order, PaymentOption


admin.site.register(Order)
admin.site.register(PaymentOption)