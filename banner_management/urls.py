from .views import *
from django.urls import path
from .views import *
urlpatterns = [
    path('backend/banner/', banner_list, name='banner_list'),
    path('backend/banner/add/', add_banner, name='add_banner'),
    path('backend/banner/activate/<int:add_id>/', activate_add, name='activate_ban'),
    path('backend/banner/deactivate/<int:add_id>/', deactivate_add, name='deactivate_ban'),
    path('backend/banner/delete/<int:add_id>/', delete_add, name='delete_ban'),
    path('backend/banner/view/<int:add_id>/', view_add, name='view_ban'),
    path('backend/banner/update/<int:add_id>/', update_add, name='update_ban'),
    path('backend/banner/edit/<int:add_id>/', edit_add, name='edit_ban'),
    path('api/banners/', BannerByCategoryAPIView.as_view(), name='banner_by_category'),
]