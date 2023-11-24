from django.urls import path
from Setting.Views.views import *

urlpatterns = [
    path('add-setting/', addSetting, name='add_setting'),
    path('update-setting/<str:setting_key>/', updateSetting, name='update_setting'),
    path('get-setting/<str:setting_key>/', getSetting, name='get_setting'),
    path('delete-setting/<str:setting_key>/', deleteSetting, name='delete_setting'),
]