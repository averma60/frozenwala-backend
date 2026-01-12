# In your models.py

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, Group, Permission
from django.db import models
from ecomApp.models import CustomUser
class Address(models.Model):
    id = models.AutoField(primary_key=True)
    user_id=models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    newname = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    status = models.CharField(max_length=50)
    delivery_time=models.CharField(max_length=50)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.newname

class AddressAdmin(models.Model):
    id = models.AutoField(primary_key=True)
    newname = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    status = models.CharField(max_length=50)
    gstn = models.CharField(max_length=50, null=True, blank=True)
    gst_rate = models.FloatField(default=18)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.newname

class ReferralLink(models.Model):
    referral_code = models.CharField(max_length=20)
    ip_address = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.referral_code