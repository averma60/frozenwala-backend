from django.urls import path
from .views import SendNotificationAPI,GetNotificationsAPI,GetUnreadNotificationsCountAPI,MarkNotificationsAsReadAPI

urlpatterns = [
    path('send-notification/', SendNotificationAPI.as_view(), name='send_notification'),
    path('api/notifications/', GetNotificationsAPI.as_view(), name='get_notifications'),
    path('api/notifications/unread/count/', GetUnreadNotificationsCountAPI.as_view(), name='unread_notifications_count'),
    path('api/notifications/mark_as_read/', MarkNotificationsAsReadAPI.as_view(), name='mark_notifications_as_read'),

]
