from Transaction.Requests.ConfigDISB import *
from BaseApi.MTN_MOMO_CONFIG import *

def userBasicInfoRequestRequest(accountHolderMSISDN):
    BASE_URL = CONFIG_MOMO_API.BASE_URL.value
    VERSION = CONFIG_MOMO_API.VERSION.value
    SERVICE = CONFIG_MOMO_API.SERVICE_DISBURSEMENT.value

    try:
        api_url = f"{BASE_URL}{SERVICE}/{VERSION}/accountholder/msisdn/{accountHolderMSISDN}/basicuserinfo"
        response = requests.get(api_url, headers=getHeader(), params={})
        if response and response.status_code == 200:
            return response
        else:
            return None
    except requests.exceptions.RequestException as e:
        return None
    return None

def checkTransactionStatus(transaction_id):
    BASE_URL = CONFIG_MOMO_API.BASE_URL.value
    VERSION = CONFIG_MOMO_API.VERSION.value
    SERVICE = CONFIG_MOMO_API.SERVICE_DISBURSEMENT.value

    api_url = f"{BASE_URL}{SERVICE}/{VERSION}/transfer/{transaction_id}"
    headers = getMomoApiHeaders()

    try:
        response = requests.get(api_url, headers=headers)

        if response and response.status_code == 200:
            return True, response.json()
        else:
            return False
    except requests.exceptions.RequestException as e:
        return False