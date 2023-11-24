from Account.models import Users
from datetime import datetime, timedelta
from BaseApi.AppEnum import *
from Abonnement.models import TontinierAbonnement


def setUserStatus(user_id):
    user = Users.objects.get(id=user_id)
    if user.account_type != AccountTypeEnum.ADMIN.value and user.account_type != AccountTypeEnum.TONTINE.value:
        user.account_type = AccountTypeEnum.TONTINE.value
        user.save()
    return True

def abonnementIsActiveAndValidate(user_id):
    return True if TontinierAbonnement.objects.filter(
            tontinier=user_id, 
            is_default=True, 
            status_abonnement=StatusAbonnementEnum.IN_PROGRESS.value, 
            transaction_state=AbonnementTransactionStatusEnum.PAYE.value, 
            expired_date__gte=datetime.now()
        ).exists() else False