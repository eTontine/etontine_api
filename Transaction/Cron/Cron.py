from Abonnement.models import Abonnement, TontinierAbonnement
from BaseApi.AppEnum import *
from Transaction.Requests.General import checkTransactionStatus
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
from TontineRule.models import Rule_values

def getGroupePenality(groupe_id):
    pernality_value = Rule_values.objects.filter(carte_or_groupe_id=groupe_id, type=TypeRuleEnum.GROUPES.value, rule__key='PENALITY_PAYMENT').first()
    if pernality_value:
        return pernality_value.value
    return 0

def checkAbonnementTransactionValidation():
    with transaction.atomic():
        filters = Q(
            Q(
                Q(transaction_status=StatusTransactionEnum.PENDING.value) | 
                Q(transaction_status=StatusTransactionEnum.PROCESSING.value)
            ) & Q(
                transaction_state=AbonnementTransactionStatusEnum.NO_PAYE.value, 
                status_abonnement=StatusAbonnementEnum.NO_VALIDATE.value
            )
        )
        abonnements = TontinierAbonnement.objects.filter(filters)

        if abonnements.exists():
            for abonnement in abonnements:
                transaction_status, abonnementTransaction = checkTransactionStatus(abonnement.referenceId)
                if transaction_status:
                    abonnement.transaction_state = AbonnementTransactionStatusEnum.PAYE.value
                    abonnement.transaction_status = abonnementTransaction['status']
                    abonnement.reseau_transaction_id = abonnementTransaction['financialTransactionId']
                    abonnement.expired_date = timezone.now() + timedelta(days=abonnement.abonnement.duration_days)
                    abonnement.status_abonnement = StatusAbonnementEnum.IN_PROGRESS.value
                    abonnement.save()
        return True

def checkCarteBuyTransactionValidation():
    with transaction.atomic():
        filters = Q(
            Q(
                Q(transaction_status=StatusTransactionEnum.PENDING.value) | 
                Q(transaction_status=StatusTransactionEnum.PROCESSING.value)
            )
        )
        carteBuys = Associate_carte.objects.filter(filters)
        if carteBuys.exists():
            for carteBuy in carteBuys:
                if carteBuy.referenceId is not None:
                    transaction_status, carteBuyTransaction = checkTransactionStatus(carteBuy.referenceId)
                    if transaction_status:
                        carteBuy.transaction_status = carteBuyTransaction['status']
                        carteBuy.reseau_transaction_id = carteBuyTransaction['financialTransactionId']
                        carteBuy.save()
        return True

def checkParticipationTontineTransactionValidation():
    with transaction.atomic():
        filters = Q(
            Q(
                Q(status=StatusTransactionEnum.PENDING.value) |
                Q(status=StatusTransactionEnum.PROCESSING.value)
            )
        )
        tontineTransactions = Transaction.objects.filter(filters)
        if tontineTransactions.exists():
            for tontineTransaction in tontineTransactions:
                if tontineTransaction.referenceId is not None:
                    transaction_status, tontineTransactionData = checkTransactionStatus(tontineTransaction.referenceId)
                    if transaction_status:
                        tontineTransaction.status = tontineTransactionData['status']
                        tontineTransaction.reseau_transaction_id = tontineTransactionData['financialTransactionId']
                        tontineTransaction.save()
                        if tontineTransaction.type_de_tontine == TontineTypeEnum.GROUPE.value and tontineTransactionData['status'] == StatusTransactionEnum.SUCCESSFUL.value and tontineTransaction.type_transaction == TypeTransactionEnum.CONTRIBUTION.value:
                            updatePaymentPeriod(tontineTransaction.object, tontineTransaction.verification_payment_date, tontineTransaction.payment_date, tontineTransaction.number_payment)
                        if tontineTransaction.type_transaction == TypeTransactionEnum.COLLECTED.value and tontineTransactionData['status'] == StatusTransactionEnum.SUCCESSFUL.value:
                            groupeOrCarteAssociate = tontineTransaction.id_association
                            groupeOrCarteAssociate.status = StatusTontinierEnum.COLLECTED.value
                            groupeOrCarteAssociate.save()
        return True

def updatePaymentPeriod(object_id, verification_payment_date, current_date, number_payment):
    with transaction.atomic():
        associateGroupe = get_object_or_404(Groupe_associate, id=object_id)
        amount = associateGroupe.groupe.amount
        paymentDates = PaymentPeriod.objects.filter(groupe_associate=associateGroupe.id, status=False, payment_date__gte=verification_payment_date).order_by('payment_date')[:number_payment]
        
        penalityValue = getGroupePenality(associateGroupe.groupe.id)
        totalAmount = amount * number_payment
        current_string_date = str(verification_payment_date)
        current_date = datetime.strptime(current_string_date, '%Y-%m-%d %H:%M:%S%z')

        for paymentDate in paymentDates:
            date_string = str(paymentDate.payment_date)
            payment_date = datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S%z')
            if payment_date < current_date:
                totalAmount += penalityValue
                paymentDate.is_pay_penality = True
            paymentDate.status = True
            paymentDate.save()