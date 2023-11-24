from Transaction.Requests.Config import *
from BaseApi.MTN_MOMO_CONFIG import *

def userBasicInfoRequest(accountHolderMSISDN):
    BASE_URL = CONFIG_MOMO_API.BASE_URL.value
    VERSION = CONFIG_MOMO_API.VERSION.value

    try:
        api_url = f"{BASE_URL}collection/{VERSION}/accountholder/msisdn/{accountHolderMSISDN}/basicuserinfo"
        response = requests.get(api_url, headers=getHeader(), params={})
        return response
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

    api_url = f"{BASE_URL}collection/{VERSION}/requesttopay/{transaction_id}"
    headers = getMomoApiHeaders()

    try:
        response = requests.get(api_url, headers=headers)

        if response and response.status_code == 200:
            return True, response.json()
        else:
            return False
    except requests.exceptions.RequestException as e:
        return False