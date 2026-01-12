from django.urls import path

from .views import *

urlpatterns = [
    path('backend/orderapp/', orderlist, name="orderapp"),
    path('backend/confirmorderapp/', confirmorderlist, name="confirmorderapp"),
    path('backend/orderapp/view_item/<str:myid>/', view_item, name="orderapp/view_item"),
    # path('api/order/<int:pk>/', OrderList.as_view(), name='order-detail'),
    path('api/order/', OrderView.as_view(), name='user-order'),
    path('backend/orderapp/activate_catagory/<int:catagory_id>/', activate_catagory,name='orderapp/activate_catagory'),
    path('backend/orderapp/deactivate_catagory/<int:catagory_id>/', deactivate_catagory,name='orderapp/deactivate_catagory'),
    path('backend/orderapp/suspend_user/<int:catagory_id>/', suspend_user, name='orderapp/suspend_user'),
    path('backend/orderapp/deliver/<int:catagory_id>/', deliver, name='orderapp/deliver'),
    path('backend/orderapp/cancel/<int:catagory_id>/', cancel, name='orderapp/cancel'),
    # path('backend/orderapp/returnrequest/<int:catagory_id>/', returnrequest, name='orderapp/returnrequest'),
    # path('backend/orderapp/returnaccepted/<int:catagory_id>/', returnaccepted, name='orderapp/returnaccepted'),
    path('update_status/<int:id>/', update_status, name='newupdate_status'),

    path('api/create_order/', create_order, name='create_order'),
    path('api/verify_payment/', verify_payment, name='verify_payment'),
    path('api/orders/', OrderListAPIView.as_view(), name='grouped-order-list'),
    path('api/invoice/', OrderDetailsAPIView.as_view(), name='grouped-order-list'),

    path('api/generate_invoice/', generate_invoice, name='generate_invoice'),
    
    path('api/payment-options/', PaymentOptionListCreateView.as_view()),
    
    path('api/order/<str:order_id>/invoice/', DownloadOrderInvoice.as_view(), name='order_invoice')

    # path('api/create_order/', create_order, name='create_order')
    # ... other URLs
]
