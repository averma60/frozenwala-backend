from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import Group, Permission
from order.models import Order
# from django.core.validators import UnicodeUsernameValidator
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from ecomApp.models import CustomUser
from django.core.validators import MinValueValidator, MaxValueValidator

class InfluencerManager(BaseUserManager):
    def create_user(self, email, phone, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, phone, password, **extra_fields)

class Influencer(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=255)
    otp_value = models.CharField(max_length=6, blank=True)
    passbook = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, unique=True, validators=[UnicodeUsernameValidator()])
    password = models.CharField(max_length=128)
    address = models.TextField()
    type = models.CharField(max_length=10)
    otp = models.CharField(max_length=10,null=True)
    commission = models.DecimalField(max_digits=10, decimal_places=2)
    code = models.CharField(max_length=50, unique=True)
    status = models.BooleanField(default=True)
    is_influencer = models.BooleanField(default=True)
    created_date=models.DateField(auto_now_add=True)

    # Required fields for AbstractBaseUser
    last_login = models.DateTimeField(default=timezone.now)

    objects = InfluencerManager()

    USERNAME_FIELD = 'phone'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['phone']

    def __str__(self):
        return self.name

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.name

    @property
    def is_staff(self):
        return self.is_superuser

    # @property
    # def is_superuser(self):
    #     return self.status and self.is_staff

    @property
    def is_active(self):
        return self.status

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser

    class Meta:
        verbose_name = 'Influencer'
        verbose_name_plural = 'Influencers'

    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        related_name='influencer_groups',  # Adjust related_name to resolve clash
        related_query_name='influencer_group',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        related_name='influencer_user_permissions',  # Adjust related_name to resolve clash
        related_query_name='influencer_user_permission',
    )


class InfluencerOtp(models.Model):
    # user = models.ForeignKey(Influencer, on_delete=models.CASCADE,null=True)
    user = models.ForeignKey(Influencer, on_delete=models.CASCADE)

    email_verified = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, blank=True)
    otp_created_at = models.DateTimeField(null=True, blank=True)
    phone_number=models.CharField(max_length=20, blank=True)

class InfluencerAmount(models.Model):
    influencer = models.ForeignKey(Influencer, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_date = models.DateTimeField(auto_now_add=True)

@receiver(pre_save, sender=Order)
def track_payment_id_change(sender, instance, **kwargs):
    if instance.pk:
        try:
            previous = Order.objects.get(pk=instance.pk)
            instance._previous_payment_id = previous.payment_id
        except Order.DoesNotExist:
            instance._previous_payment_id = None
    else:
        instance._previous_payment_id = None

@receiver(post_save, sender=Order)
def send_commission_to_influencer(sender, instance, **kwargs):
    if instance.influencer_code and instance.payment_id:
        # Check if payment_id was updated and if no commission has been credited for this order yet
        if (hasattr(instance, '_previous_payment_id') and
                instance.payment_id != instance._previous_payment_id):
            try:
                influencer = Influencer.objects.get(code=instance.influencer_code)
                commission_amount = (float(instance.total_price) * float(influencer.commission)) / 100  # assuming commission is a percentage

                # Check if this payment_id has been processed before
                if not InfluencerAmount.objects.filter(order__payment_id=instance.payment_id).exists():
                    # Create a new InfluencerAmount record
                    InfluencerAmount.objects.create(
                        influencer=influencer,
                        order=instance,
                        amount=commission_amount
                    )
            except Influencer.DoesNotExist:
                pass


class InfluencerLink(models.Model):
    influencer_code = models.CharField(max_length=20)
    ip_address = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.influencer_code

class InfluencerRecord(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="influencer_records"
    )

    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    benefit_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100),
        ],
        help_text="Percentage benefit (0–100)"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.phone_number} ({self.benefit_percentage}%)"
