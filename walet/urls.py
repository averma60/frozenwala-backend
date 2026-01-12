from django.urls import path
from .views import *
urlpatterns = [
    path('api/wallet/', WalletAPIView.as_view(), name='wallet_api'),
    path('api/save_wallet_transaction/', UpdateWallet.as_view(), name='save_wallet_transaction'),
     path('api/wallet/transactions/', WalletTransactionAPIView.as_view(), name='WalletTransactionAPIView'),
    

    path('backend/purchase_benefits/', purchase_benefit_list, name='purchase_benefit_list'),
    path('backend/purchase_benefits/add/', add_purchase_benefit, name='add_purchase_benefit'),
    path('backend/purchase_benefits/<int:benefit_id>/activate/', activate_purchase_benefit, name='activate_purchase_benefit'),
    path('backend/purchase_benefits/<int:benefit_id>/deactivate/', deactivate_purchase_benefit,
         name='deactivate_purchase_benefit'),
    path('backend/purchase_benefits/<int:benefit_id>/delete/', delete_purchase_benefit, name='delete_purchase_benefit'),
    path('backend/purchase_benefits/<int:benefit_id>/', view_purchase_benefit, name='view_purchase_benefit'),
    path('backend/purchase_benefits/<int:benefit_id>/edit/', update_purchase_benefit, name='update_purchase_benefit'),
    path('backend/purchase_benefits/<int:benefit_id>/edit/', edit_purchase_benefit, name='edit_purchase_benefit'),

    path('backend/installation_benefit/list/', installation_benefit_list, name='installation_benefit_list'),
    path('backend/installation_benefit/add/', add_installation_benefit, name='add_installation_benefit'),
    path('backend/installation_benefit/activate/<int:benefit_id>/', activate_installation_benefit,
         name='activate_installation_benefit'),
    path('backend/installation_benefit/deactivate/<int:benefit_id>/', deactivate_installation_benefit,
         name='deactivate_installation_benefit'),
    path('backend/installation_benefit/delete/<int:benefit_id>/', delete_installation_benefit,
         name='delete_installation_benefit'),
    path('backend/installation_benefit/view/<int:benefit_id>/', view_installation_benefit, name='view_installation_benefit'),
    path('backend/installation_benefit/update/<int:benefit_id>/', update_installation_benefit,
         name='update_installation_benefit'),

    # Referral Benefit URLs
    path('backend/referral_benefit/list/', referral_benefit_list, name='referral_benefit_list'),
    path('backend/referral_benefit/add/', add_referral_benefit, name='add_referral_benefit'),
    path('backend/referral_benefit/activate/<int:benefit_id>/', activate_referral_benefit, name='activate_referral_benefit'),
    path('backend/referral_benefit/deactivate/<int:benefit_id>/', deactivate_referral_benefit,
         name='deactivate_referral_benefit'),
    path('backend/referral_benefit/delete/<int:benefit_id>/', delete_referral_benefit, name='delete_referral_benefit'),
    path('backend/referral_benefit/view/<int:benefit_id>/', view_referral_benefit, name='view_referral_benefit'),
    path('backend/referral_benefit/update/<int:benefit_id>/', update_referral_benefit, name='update_referral_benefit'),
    path('api/remove_wallet/', RemoveWallet.as_view(), name='remove_wallet'),
    path('api/wallet-benefits/', WalletBenefitListAPIView.as_view(), name='wallet_benefits_api'),
    path('api/wallet-order/', CreateWalletOrderAPIView.as_view(), name='create_wallet_order'),
    path('api/verify-wallet-order/', VerifyWalletOrderAPIView.as_view(), name='create_wallet_order'),
    path('api/purchase-benefits/', PurchaseBenefitListAPIView.as_view(), name='purchase_benefits_api'),

    # Other URL patterns...
]
