from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Otp,CustomerCoupon,Product,Catagory,Stock
class CustomUserAdmin(UserAdmin):
    list_display = ('phone_number','influencer_code','is_influencer','otp_value','status','referral_code', 'name','registration_id','walet', 'is_active', 'is_staff')
    list_filter = ('is_active', 'is_staff')
    search_fields = ('phone_number', 'name', 'referral_code')
    ordering = ('phone_number',)

    fieldsets = (
        (None, {'fields': ('phone_number','influencer_code','is_influencer', 'referral_code','email','otp_value', 'password','status')}),
        ('Personal Info', {'fields': ('name', 'level','profile_photo','bio','walet','registration_id')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number','otp_value', 'name', 'email','referral_code', 'password1', 'password2'),
        }),
    )

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Otp)
admin.site.register(CustomerCoupon)
admin.site.register(Product)
admin.site.register(Catagory)

admin.site.register(Stock)

