from django.urls import path
from Transaction.Views.views import *
from Transaction.Views.Groupe import *
from Transaction.Views.Carte import *

urlpatterns = [
    path("test-momo-api/<str:phone>", testApiMomo, name="test-momo-api"),
    path("launch-cron", launchCron, name="launch-cron"),

    # Participation Tontine Groupe
    path('get-groupe-payment-detail', getPaymentDetails),
    path('send-tontine-groupe-contribution', addGroupeAssociateTransaction),

     # Participation Tontine Carte
    path('get-carte-payment-detail', getCartePaymentDetails),
    path('send-carte-contribution', addCarteAssociateTransaction)
]