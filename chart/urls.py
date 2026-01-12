from .views import *
from django.urls import path

urlpatterns = [
    path('backend/daywise-chart/', daywise_chart, name='daywise_chart'),
    path('backend/render_product_dropdown/', render_product_dropdown, name='render_product_dropdown'),
    path('backend/itemwise-chart/', itemwise_chart, name='itemwise_chart'),
    path('backend/daily_chart/', daily_chart, name='daily_chart'),
    path('backend/category_wise_sales_chart/', category_wise_sales_chart, name='category_wise_sales_chart'),
    path('backend/profit_chart/', profit_chart, name='profit_chart'),

]