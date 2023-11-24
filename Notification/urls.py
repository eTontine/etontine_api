from django.urls import path
from Notification.views import *

urlpatterns = [
    path('user_notifications', user_notifications, name='user_notifications'),
    path('notification_details/<int:notification_id>', notification_details, name='notification_details'),
    path('notification_vues/<int:notification_id>', notification_vues, name='notification_vues'),
    path('notification_send/<int:notification_id>', notification_send, name='notification_send'),
    path('create_notification', create_notification, name='create_notification')
]