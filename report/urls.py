from .views import *
from django.urls import path

urlpatterns = [
    path('backend/daywise-report/', daywise_report, name='daywise_report'),
    path('backend/render_product_dropdown/', render_product_dropdown, name='render_product_dropdown'),
    path('backend/itemwise-report/', itemwise_report, name='itemwise_report'),
    path('backend/daily_sale/', daily_sale, name='daily_sale'),
    path('backend/category_wise_sales_report/', category_wise_sales_report, name='category_wise_sales_report'),
    path('backend/profit_report/', profit_report, name='profit_report'),

]