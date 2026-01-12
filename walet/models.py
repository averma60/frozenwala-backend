from django.db import models
from ckeditor.fields import RichTextField
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.
class Walet(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.IntegerField(unique=True)
    wallet_value = models.FloatField(default=0.0)


class WalletTransaction(models.Model):
    id = models.BigAutoField(primary_key=True)
    user_id = models.IntegerField()
    transaction_id = models.CharField(max_length=255, null=True, blank=True)
    opening_bal = models.DecimalField(max_digits=13, decimal_places=2)
    credit_bal = models.DecimalField(max_digits=13, decimal_places=2)
    debit_bal = models.DecimalField(max_digits=13, decimal_places=2)
    closing_bal = models.DecimalField(max_digits=13, decimal_places=2)
    transaction_type = models.CharField(max_length=155)
    wallet_benefit = models.PositiveIntegerField(default=0, help_text="Extra benefit amount given")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'wallet_transaction' 


class PurchaseBenefit(models.Model):
    id = models.AutoField(primary_key=True)
    status = models.CharField(max_length=50,default='1')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    benefit_percentage = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"PurchaseBenefit #{self.id}"


from django.db import models

class InstallationBenefit(models.Model):
    id = models.AutoField(primary_key=True)
    price = models.CharField(max_length=50,blank=True)
    status = models.CharField(max_length=50, default='1')

    def __str__(self):
        return f"Installation Benefit - {self.price} "


class ReferralBenefit(models.Model):
    id = models.AutoField(primary_key=True)
    price = models.CharField(max_length=50,blank=True)
    status = models.CharField(max_length=50, default='1')

    def __str__(self):
        return f"Referral Benefit - {self.price} "

class WalletBenefit(models.Model):
    add_amount = models.PositiveIntegerField(
        unique=True,
        help_text="Amount user needs to add to wallet"
    )
    benefit_amount = models.PositiveIntegerField(
        help_text="Extra benefit amount given"
    )

    description = RichTextField()

    influencer = models.BooleanField(
        default=False,
        help_text="Is this benefit only for influencers?"
    )

    influencer_time_period = models.DurationField(
        null=True,
        blank=True,
        help_text="Validity period for influencer benefits (e.g. 7 days)"
    )

    influencer_benefit_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100),
        ],
        help_text="Percentage benefit (0–100)"
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-add_amount']

    def __str__(self):
        return f"Add ₹{self.add_amount} → Get ₹{self.benefit_amount}"
