from .views import *
from django.urls import path

urlpatterns = [

    path('backend/dashboard', dashboard , name="backend/dashboard"),
    path('backend/charts', charts , name="backend/charts"),
    path('backend/verify-email/', verify_email, name='backend/verify_email'),
    path('backend/verify-otp/', verify_otp, name='verify_otp'),
    path('backend/change-password/', change_password, name='change_password'),

    # path('backend/userlist/share_income/<int:myid>/', share_income, name='userlist/share_income'),
     path('backend/catagoryapp/', catagory, name="catagoryapp"),
     path('backend/catgoryadd/', catgoryadd, name="catgoryadd"),
     path('backend/catagoryapp/delete_item/<int:myid>/', delete_item, name="catagory/delete_item"),
     path('backend/catagoryapp/edit_item/<int:myid>/', edit_item, name="catagory/edit_item"),
     path('backend/catagoryapp/update_item/<int:myid>/', update_item, name="catagory/update_item"),
     path('backend/catagoryapp/view_item/<int:myid>/', view_item, name="catagory/view_item"),
     path('backend/catagoryapp/activate_catagory/<int:catagory_id>/', activate_catagory, name='catgoryapp/activate_catagory'),
     path('backend/catagoryapp/deactivate_catagory/<int:catagory_id>/', deactivate_catagory, name='catgoryapp/deactivate_catagory'),


    path('backend/productapp/', product, name="productapp"),
     path('backend/productadd/', productadd, name="productadd"),
     path('backend/productapp/delete_item/<int:myid>/', delete_product, name="delete_item"),
     path('backend/productapp/edit_item/<int:myid>/', edit_product, name="edit_item"),
     path('backend/productapp/update_item/<int:myid>/', update_product, name="update_item"),
     path('backend/productapp/view_item/<int:myid>/', view_product, name="view_item"),
     path('backend/productapp/activate_product/<int:product_id>/', activate_product, name='productapp/activate_product'),
     path('backend/productapp/deactivate_product/<int:product_id>/', deactivate_product, name='productapp/deactivate_product'),


    path('backend/customerlist/', customerlist, name="customerlist"),
    path('backend/customerlist/activate_product/<int:id>/', activate_customer, name='customerlist/activate_customer'),
    path('backend/customerlist/deactivate_product/<int:id>/', deactivate_customer,name='customerlist/deactivate_customer'),

    path('backend/customer_couponlist/', customer_couponlist, name='customer_couponlist'),
    path('backend/customer_couponlist/add_customer_coupon/', add_customer_coupon, name='add_customer_coupon'),
    path('backend/customer_couponlist/delete_item/<int:coupon_id>/', delete_coupon, name="customer_couponlist/delete_item"),
    path('backend/customer_couponlist/activate_coupon/<int:coupon_id>/', activate_coupon, name='customer_couponlist/activate_coupon'),
    path('backend/customer_couponlist/deactivate_coupon/<int:coupon_id>/', deactivate_coupon,
         name='customer_couponlist/deactivate_coupon'),

    path('backend/chargeapp/', charge, name="chargeapp"),
    path('backend/payment-options/', payment_options, name="payment_options"),
    path('backend/chargeadd/', chargeadd, name="chargeadd"),
    path('backend/payment_options_add/', payment_options_add, name="payment_options_add"),
    path('backend/chargeapp/delete_item/<int:myid>/', delete_charge, name="delete_charge"),
    path('backend/chargeapp/edit_item/<int:myid>/', edit_charge, name="edit_charge"),
    path('backend/edit_payment_option/<int:id>/', edit_payment_option, name="edit_payment_option"),
    path('backend/delete_payment_option/<int:id>/', delete_payment_option, name="delete_payment_option"),
    path('backend/chargeapp/update_item/<int:myid>/', update_charge, name="update_charge"),

    path('backend/inventory_list/', stock, name="stock"),
    path('api/stock/', StockListAPIView.as_view(), name='stock-list'),
    path('backend/stock/edit_item/<int:myid>/', edit_stock, name="edit_stock"),
    path('backend/stock/update_item/<int:stock_id>/', update_stock, name="update_stock"),
    path('backend/stock/update/', update_all_stock, name='update_all_stock'),
    path('backend/stock/all_edit_item/', allstock, name="allstock"),
    path('pending-orders/count/', pending_orders_count, name='pending_orders_count'),
    path('orders/dropdown/', render_order_dropdown, name='order_dropdown'),
    path('api/couponlist/', CouponList.as_view(), name='coupon-list'),

    path('backend/wallet-benefits/', wallet_benefits, name='wallet_benefits'),
    path('backend/add-wallet-benefit/', add_wallet_benefit, name='add_wallet_benefit'),
    path('backend/edit-wallet-benefit/<int:id>/', edit_wallet_benefit, name='edit_wallet_benefit'),
    path('backend/delete-wallet-benefit/<int:id>/', delete_wallet_benefit, name='delete_wallet_benefit'),

]
