from django.contrib import admin
from .models import Cart,CartCoupon, Whishlist
# Register your models here.
admin.site.register(Cart)
admin.site.register(CartCoupon)
admin.site.register(Whishlist)
