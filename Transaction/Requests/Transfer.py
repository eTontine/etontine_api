from Transaction.Requests.ConfigDISB import *
from BaseApi.MTN_MOMO_CONFIG import *
from decimal import Decimal

def initiateUserDisbursement(receiver_phone, amount, message, externalId, referentId):
    BASE_URL = CONFIG_MOMO_API.BASE_URL.value
    VERSION = CONFIG_MOMO_API.VERSION.value
    SERVICE = CONFIG_MOMO_API.SERVICE_DISBURSEMENT.value
    headers = getMomoApiHeaders(str(referentId))

    disbursement_url = f"{BASE_URL}{SERVICE}/{VERSION}/transfer"

    payload = {
        "amount": amount, 
        "currency": CONFIG_MOMO_API.DEFAULT_CURRENCY.value,
        "externalId": externalId,
        "payee": {
            "partyIdType": "MSISDN",
            "partyId": receiver_phone,
        },
        "payerMessage": message,
        "payeeNote": message,
    }

    try:
        response = requests.post(disbursement_url, headers=headers, json=payload)

        if response and response.status_code == 202:
            return True, response.status_code
        else:
            return False, response.status_code
    except requests.exceptions.RequestException as e:
        return False, f"Message : {str(e)}"