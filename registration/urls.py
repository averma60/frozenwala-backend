
from .views import *
from django.urls import path

urlpatterns = [
    path('register/', RegistrationView.as_view(), name='register'),
    path('ref/frzn/', RegistrationViewuu.as_view(), name='register'),

    path('login/', LoginView.as_view(), name='login'),

    path('api/addresses/', AddressList.as_view(), name='address-list'),
    path('api/update_delivery_time/', update_delivery_time, name='update_delivery_time'),
    path('api/profile/', ProfileAPI.as_view(), name='profile'),
    
    path('api/delete_account/', DeleteAccountAPI.as_view(), name='delete_account'),
    path('api/signout/', SignOutAPI.as_view(), name='signout'),
    path('api/send_sms/', send_sms, name='send_sms'),
    path('api/login-send_sms/', loginsend_sms, name='loginsend_sms'),

    path('api/admin/addresses/', AddressAdminList.as_view(), name='address-list'),
    path('api/admin/addresses/detail/', AddressAdminDetail.as_view(), name='address-detail'),

    path('backend/addresses/', address_list, name='back/address_list'),
    path('backend/addresses/add/', add_address, name='add_address'),
    path('backend/addresses/activate/<int:address_id>/', activate_address, name='activate_address'),
    path('backend/addresses/deactivate/<int:address_id>/', deactivate_address, name='deactivate_address'),
    path('backend/addresses/delete/<int:address_id>/', delete_address, name='delete_address'),
    path('backend/addresses/view/<int:address_id>/', view_address, name='view_address'),
    path('backend/addresses/update/<int:address_id>/', update_address, name='update_address'),
    path('backend/addresses/edit/<int:address_id>/', edit_address, name='edit_address'),
    path('api/referrals/', MyRefferals.as_view(), name='my_refferals'),
]
