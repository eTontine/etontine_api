from django.urls import path
from Account.Views.general_views import *
from Account.Views.views import *
from Account.Views.views_authenticate import *

urlpatterns = [
    path('login', LoginView.as_view(), name='login'),
    path('token/refresh', UserTokenRefreshView.as_view(), name='token_refresh'),
    path('logout', Logout.as_view(), name='logout'),
    path('register', register, name='register'),
    path('users', users, name='users'),
    path('users/<int:id>', user, name='user'),
    path('me', me, name='me'),

    path('countries', countries, name='countries'),
]