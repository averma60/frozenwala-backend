from django.contrib import admin
from django.urls import path
from django.contrib import admin
from django.urls import path
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView


urlpatterns = [
    path('', RedirectView.as_view(url='/backend/login/', permanent=False)),
    # path('backend/login/', login_view, name='backend/login'),

    path('admin/', admin.site.urls),
    path('', include('ecomApp.urls')),
    path('', include('backendlogin.urls')),
    path('', include('registration.urls')),
    path('', include('menu_management.urls')),
    path('', include('advertisement_management.urls')),
    path('', include('banner_management.urls')),
    path('', include('order.urls')),
    path('', include('walet.urls')),
    path('', include('cart.urls')),
    path('', include('report.urls')),
    path('', include('notification.urls')),
    path('', include('chart.urls')),
    path('', include('influencer.urls')),
]

if settings.DEBUG:
    urlpatterns+= static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)

