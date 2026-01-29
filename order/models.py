
from django.db import models
from django.contrib.auth.models import User
from ecomApp.models import CustomUser
from ecomApp.models import Catagory
from ecomApp.models import Product
from django.conf import settings
from menu_management.models import Item


class PaymentOption(models.Model):
    PAYMENT_TYPE_CHOICES = (
        ('cod', 'Cash On Delivery'),
        ('online', 'Online Payment'),
    )

    code = models.CharField(
        max_length=20,
        choices=PAYMENT_TYPE_CHOICES,
        unique=True
    )

    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.get_code_display()

class Order(models.Model):

    id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,null=True)#made CustomUser later
    payment_option = models.ForeignKey(PaymentOption, on_delete=models.SET_NULL, null=True)
    product_id = models.ForeignKey(Item, on_delete=models.CASCADE)
    couponcode = models.CharField(max_length=50, blank=True, null=True)
    quantity=models.IntegerField()
    price = models.FloatField()
    total_price = models.FloatField()
    payment_id = models.CharField(max_length=255)
    order_id = models.CharField(max_length=255)
    signature = models.CharField(max_length=255)
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    newname = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    delivery_time=models.CharField(max_length=50)
    order_item_id=models.CharField(max_length=50)
    influencer_code=models.CharField(max_length=90, blank=True, null=True)
    dicounted_price=models.CharField(max_length=50)
    walet_value=models.CharField(max_length=50, blank=True, null=True)
    percentage_benefit = models.FloatField(default=0.0)  # Added field for percentage benefit
    purchase_benefit = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    pick_up=models.CharField(max_length=50)
    previous_price=models.CharField(max_length=50)
    delivery_price=models.CharField(max_length=50)

    # GST fields
    gstn = models.CharField(max_length=50, null=True, blank=True)
    gst_rate = models.FloatField(default=0)
    cgst_amount = models.FloatField(default=0)
    sgst_amount = models.FloatField(default=0)
    total_gst = models.FloatField(default=0)

    order_type = models.CharField(choices=[('standard', 'Standard'), ('qr_code', 'QR Code')], max_length=10, default='standard')

    def __str__(self):
        return  f"{self.id}"
