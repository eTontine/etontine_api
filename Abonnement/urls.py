from django.contrib import admin
from django.urls import path, include
from Abonnement.Views.views import *

urlpatterns = [
    path('user-abonnements/<int:tontinier_id>', tontinierAbonnements, name='user_abonnements'),
    path('default-abonnement', tontinierDefaultAbonnement, name='default_abonnement'),
    path('abonnements', abonnements, name='abonnements'),
    path('abonnements/<int:abonnement_id>', abonnement, name='abonnement'),
    path("make-abonnement", choiceAbonnement, name="make_abonnement"),
    path('set-default-tontinier-abonnement/<int:tontinier_abonnement_id>', setDefaultAbonnement, name='set_default_tontinier_abonnement'),
]
