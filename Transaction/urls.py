from django.urls import path
from Transaction.Views.views import *
from Transaction.Views.Groupe import *
from Transaction.Views.Carte import *

urlpatterns = [
    path("test-momo-api/<str:phone>", testApiMomo, name="test-momo-api"),
    path("test-momo-api-dis/<str:phone>", testApiMomoDis, name="test-momo-api"),
    path("test-transfer", makeDisbursementTest, name="test-momo-api"),
    path("launch-cron", launchCron, name="launch-cron"),

    # Participation Tontine Groupe
    path('get-groupe-payment-detail', getPaymentDetails),
    path('send-tontine-groupe-contribution', addGroupeAssociateTransaction),

     # Participation Tontine Carte
    path('get-carte-payment-detail', getCartePaymentDetails),
    path('send-carte-contribution', addCarteAssociateTransaction),

    # Collect carte Transaction
    path('get-carte-collect-request/<int:tontinier_id>', getCarteCollectRequest),
    path('validate-carte-collect-request/<int:transaction_id>', validateCarteCollectRequest),
    path('make-carte-collect-request', makeCarteCollectRequest),
    path('send-carte-collect-transaction', sendCarteCollectTransaction),

    # Collect Groupe Transaction
    path('get-groupe-collect-not-make/<int:tontinier_id>', getGroupeCollectNoMake),
    path('send-groupe-collect-transaction', sendGroupeCollectTransaction),

    # History
    path('transactions-history', transactionHistory),
]