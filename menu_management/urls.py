
from .views import *
from django.urls import path
from .views import *
urlpatterns = [
    path('backend/items/', item_list, name='item_list'),
    # path('backend/item/add/', add_item, name='add_item'),
    # path('backend/item/activate/<int:item_id>/', activate_item, name='activate_item'),
    # path('backend/item/nonveg/<int:item_id>/', nonveg, name='nonveg'),
    # path('backend/item/veg/<int:item_id>/', veg, name='veg'),
    # path('backend/item/deactivate/<int:item_id>/', deactivate_item, name='deactivate_item'),
    # path('backend/item/delete/<int:item_id>/', delete_item, name='delete_item'),
    # path('backend/item/view/<int:item_id>/', view_item, name='view_item'),
    # path('backend/item/update/<int:item_id>/', update_item, name='update_item'),
    # path('backend/item/edit/<int:item_id>/', edit_item, name='edit_item'),

    path('backend/deal_of_the_day/', deal_of_the_day, name='deal_of_the_day'),
    path('backend/recommended/', recommended, name='recommended'),
    path('backend/most_popular/', most_popular, name='most_popular'),

    path('api/deal-of-the-day/', DealOfTheDayAPIView.as_view(), name=''),
    path('api/recommended/', RecommendedAPIView.as_view(), name=''),
    path('api/most-popular/', MostPopularAPIView.as_view(), name=''),
    path('api/product-all/', AllProduct.as_view(), name=''),
    path('api/product-detail/', ProductDetailsAPIView.as_view(), name=''),
    path('api/review/<int:item_id>/', AddOrUpdateReview.as_view(), name="add-update-review"),
    path('api/review-list/<int:item_id>/', GetItemReviews.as_view(), name="review-list"),
    path('api/category/product-all/', CategoryAPIView.as_view(), name=''),
    path('api/product/search/', SearchProductAPIView.as_view(), name=''),
    path('api/categories/', CategoryFetch.as_view(), name=''),


    path('api/categories/allpro/', CategoryProAPIView.as_view(), name=''),

    path('api/five/categories/', CategoryfiveFetch.as_view(), name=''),
    path('api/deal_of_the_day_five/', DealOfTheDayfiveAPIView.as_view(), name='deal_of_the_day_five'),
    path('api/recommended_five/', RecommendedfiveAPIView.as_view(), name='recommended_five'),
    path('api/most_popular_five/', MostPopularfiveAPIView.as_view(), name='most_popular_five'),
    path('api/all_five_product/', AllfiveProduct.as_view(), name='all_five_product'),
    path('api/search/', ItemSearchAPIView.as_view(), name='search_items'),
    path('api/auth/categories/', AuthCategoryFetch.as_view(), name=''),
    path('api/auth/most-popular/', AuthMostPopularAPIView.as_view(), name=''),
    path('api/auth/category/product-all/', AuthCategoryAPIView.as_view(), name=''),
    path('api/auth/product-all/', AuthAllProduct.as_view(), name=''),
    path('api/item/', ProductsId.as_view(), name=''),
    path('api/veg-items/', VegItemListAPIView.as_view(), name='veg-items'),
    path('api/auth/veg-items/', AuthVegItemListAPIView.as_view(), name='veg-items'),
    path('api/item-brands/', ItemBrandsAPIView.as_view(), name='item-brands'),

]


