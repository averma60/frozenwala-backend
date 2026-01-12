
from .views import *
from django.urls import path
from .views import *
urlpatterns = [
    path('backend/advertisement/', advertisement_list, name='advertisement_list'),
    path('backend/advertisement/add/', add_advertisement, name='add_advertisement'),
    path('backend/advertisement/activate/<int:add_id>/', activate_add, name='activate_add'),
    path('backend/advertisement/deactivate/<int:add_id>/', deactivate_add, name='deactivate_add'),
    path('backend/advertisement/delete/<int:add_id>/', delete_add, name='delete_add'),
    path('backend/advertisement/view/<int:add_id>/', view_add, name='view_add'),
    path('backend/advertisement/update/<int:add_id>/', update_add, name='update_add'),
    path('backend/advertisement/edit/<int:add_id>/', edit_add, name='edit_add'),
    path('api/adds/', AddByCategoryAPIView.as_view(), name='add_by_category'),
]