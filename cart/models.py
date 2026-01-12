from django.db import models

# Create your models here.
from django.db import models
from ecomApp.models import CustomUser
from menu_management.models import Item

class Cart(models.Model):
    id = models.AutoField(primary_key=True)
    product_id = models.ForeignKey(Item, on_delete=models.CASCADE)
    u_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    quantity=models.IntegerField()
    price=models.FloatField()
    status = models.CharField(max_length=20, default='Active')
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart item - ID: {self.id}"
class CartCoupon(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.IntegerField(unique=True)
    coupon_code = models.CharField(max_length=50)

class Whishlist(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Wishlist item - ID: {self.id}"
