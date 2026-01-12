from django.contrib import admin
from .models import Walet, PurchaseBenefit, ReferralBenefit, InstallationBenefit, WalletBenefit, WalletTransaction

admin.site.register(PurchaseBenefit)
admin.site.register(Walet)
admin.site.register(ReferralBenefit)
admin.site.register(InstallationBenefit)
admin.site.register(WalletBenefit)
admin.site.register(WalletTransaction)
