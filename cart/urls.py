
from .views import *
from django.urls import path
from .views import *

urlpatterns = [
    path('api/add_to_cart/', AddToCartAPIView.as_view(), name='add_to_cart'),
    path('api/get_cart/', CartDetailsAPIView.as_view(), name='get_cart'),
    path('api/get_all_coupon/', GetAllCouponAPIView.as_view(), name='get_all_coupon'),
    path("api/apply-coupon/", ApplyCouponAPIView.as_view(), name="apply_coupon"),


    path('api/get_cart/main/', CartDetailsMainAPIView.as_view(), name='get_cart'),

    path('api/increase/', IncreaseQuantity.as_view(), name='increase'),
    path('api/decrease/', DecreaseQuantity.as_view(), name='decrease'),

    path('api/increase/main/', IncreaseQuantityMain.as_view(), name=''),
    path('api/decrease/main/', DecreaseQuantityMain.as_view(), name=''),


    path('api/remove-cart-item/', RemoveCartItem.as_view(), name='remove_cart_item'),
    path('api/get_total_price/', CartTotalPrice.as_view(), name='CartTotalPrice'),

    path('api/send_coupon/', send_coupon, name='send_coupon'),
    path('api/unique-product-count/', UniqueProductCount.as_view(), name='unique_product_count'),
    
    path('api/wishlist/', WishlistAPIView.as_view(), name='wishlist')

]