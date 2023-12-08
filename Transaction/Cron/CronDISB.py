from Abonnement.models import Abonnement, TontinierAbonnement
from BaseApi.AppEnum import *
from Transaction.Requests.GeneralDISB import checkTransactionStatus
from django.utils.timezone import timedelta, datetime
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from django.db.models import Q
from Transaction.models import Transaction
from django.db import transaction
from BaseApi.AppEnum import *
import pytz
from django.shortcuts import get_object_or_404
from Tontine.models import *
from Transaction.Requests.Payment import *
from Transaction.Requests.Transfer import *

def makeDisbursement():
    with transaction.atomic():
        transactions_to_disburse = Transaction.objects.filter(
            is_transfert_to_tontinier=False,
            receiver_data__external_id__isnull=True,
            receiver_data__referenceId__isnull=True
        )

        for transactionData in transactions_to_disburse:
            external_id = getExternalIdUnique()
            referentId = getUniqueReferenceUuid()
            amount = float(transactionData.amount)
            transfer_status, response = initiateUserDisbursement(transactionData.receiver_phone, amount, f'Transfer', external_id, referentId)
            if transfer_status:
                receiver_data = {
                    "external_id": str(external_id),
                    "referenceId": str(referentId),
                    "status": StatusTransactionEnum.PENDING.value,
                    "amount": float(transactionData.amount),
                    "receiver_phone": transactionData.receiver_phone
                }
                transactionData.receiver_data = receiver_data
                transactionData.save()
            print(f'Transaction {transactionData.id} successfully disbursed')
            
def setTransferToTontinierStatus():
    with transaction.atomic():
        transactions_to_disburse = Transaction.objects.filter(
            is_transfert_to_tontinier=False,
            receiver_data__external_id__isnull=False,
            receiver_data__referenceId__isnull=False,
            receiver_data__status=StatusTransactionEnum.PENDING.value
        )

        for transactionData in transactions_to_disburse:
            referenceId = transactionData.receiver_data.get('referenceId')
            if referenceId is not None:
                transfer_status, response = checkTransactionStatus(referenceId)
                if transfer_status:
                    transactionData.receiver_data['status'] = StatusTransactionEnum.SUCCESSFUL.value
                    transactionData.is_transfert_to_tontinier = True
                    transactionData.save()
                    print(f'Transaction {transactionData.id} successfully transferred')
                else:
                    print(f'Transaction {transactionData.id} not transferred')