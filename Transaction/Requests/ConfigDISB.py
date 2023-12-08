from Setting.models import Setting
from BaseApi.MTN_MOMO_CONFIG import CONFIG_MOMO_API
import requests
import base64
import string
import random
import uuid
from datetime import datetime, timedelta
from Transaction.models import Transaction
from Abonnement.models import TontinierAbonnement
from Tontine.models import Associate_carte

def getAppOCPAPIM_X_REFERENCE_ID():
    OCP_APIM_SUBSCRIPTION_KEY_DISBURSEMENT = CONFIG_MOMO_API.OCP_APIM_SUBSCRIPTION_KEY_DISBURSEMENT.value
    X_REFERENCE_ID = CONFIG_MOMO_API.X_REFERENCE_ID.value

    OCP_APIM_SUBSCRIPTION_KEY_DISBURSEMENT, create = Setting.objects.get_or_create(key="OCP_APIM_SUBSCRIPTION_KEY_DISBURSEMENT", defaults={"value": OCP_APIM_SUBSCRIPTION_KEY_DISBURSEMENT})
    OCP_APIM_SUBSCRIPTION_KEY_DISBURSEMENT = OCP_APIM_SUBSCRIPTION_KEY_DISBURSEMENT.value

    X_REFERENCE_ID, create = Setting.objects.get_or_create(key="X_REFERENCE_ID", defaults={"value": X_REFERENCE_ID})
    X_REFERENCE_ID = X_REFERENCE_ID.value
    
    return OCP_APIM_SUBSCRIPTION_KEY_DISBURSEMENT, X_REFERENCE_ID

def getApiKey():
    OCP_APIM_SUBSCRIPTION_KEY_DISBURSEMENT, X_REFERENCE_ID = getAppOCPAPIM_X_REFERENCE_ID()
    BASE_API_URL = CONFIG_MOMO_API.BASE_URL.value + CONFIG_MOMO_API.VERSION.value + "/apiuser/" + X_REFERENCE_ID + "/apikey"
    headers = {
        "Ocp-Apim-Subscription-Key": OCP_APIM_SUBSCRIPTION_KEY_DISBURSEMENT,
    }

    response = requests.post(BASE_API_URL, headers=headers)
    if response and response.status_code == 201:
        api_key = response.json().get("apiKey")
        Setting.objects.update_or_create(key="API_KEY_DISBURSEMENT", defaults={"value": api_key})
        return api_key
    else:
        return None

def getUserMomoToken():
    try:
        OCP_APIM_SUBSCRIPTION_KEY_DISBURSEMENT = Setting.objects.get(key="OCP_APIM_SUBSCRIPTION_KEY_DISBURSEMENT")
        X_REFERENCE_ID = Setting.objects.get(key="X_REFERENCE_ID")
        API_KEY_DISBURSEMENT = Setting.objects.get(key="API_KEY_DISBURSEMENT") 
    except Setting.DoesNotExist:
        OCP_APIM_SUBSCRIPTION_KEY_DISBURSEMENT, X_REFERENCE_ID = getAppOCPAPIM_X_REFERENCE_ID()
        API_KEY_DISBURSEMENT = getApiKey()

    if OCP_APIM_SUBSCRIPTION_KEY_DISBURSEMENT and X_REFERENCE_ID and API_KEY_DISBURSEMENT:
        OCP_APIM_SUBSCRIPTION_KEY_DISBURSEMENT = OCP_APIM_SUBSCRIPTION_KEY_DISBURSEMENT.value
        X_REFERENCE_ID = X_REFERENCE_ID.value
        API_KEY_DISBURSEMENT = API_KEY_DISBURSEMENT.value

        BASE_API_URL = f'{CONFIG_MOMO_API.BASE_URL.value}{CONFIG_MOMO_API.SERVICE_DISBURSEMENT.value}/token/'
        auth_header = base64.b64encode(f"{X_REFERENCE_ID}:{API_KEY_DISBURSEMENT}".encode('utf-8')).decode('utf-8')

        headers = {
            "Ocp-Apim-Subscription-Key": OCP_APIM_SUBSCRIPTION_KEY_DISBURSEMENT,
            "X-Target-Environment": CONFIG_MOMO_API.X_TARGET_ENVIRONMENT.value,
            "Authorization": f"Basic {auth_header}"
        }

        try:
            response = requests.post(BASE_API_URL, headers=headers)
            if response.status_code != 200:
                getApiKey()
                getUserMomoToken()
            if response and response.status_code == 200:
                token_info = response.json()
                access_token = token_info.get("access_token")
                expires_in = token_info.get("expires_in")
                token_type = token_info.get("token_type")
                created_at_token = datetime.now()
                expires_at_date = created_at_token + timedelta(seconds=int(expires_in))

                Setting.objects.update_or_create(key="MOMO_ACCESS_TOKEN_DISBURSEMENT", defaults={"value": access_token})
                Setting.objects.update_or_create(key="MOMO_ACCESS_TOKEN_EXP_DISBURSEMENT", defaults={"value": expires_in})
                Setting.objects.update_or_create(key="MOMO_TOKEN_TYPE_DISBURSEMENT", defaults={"value": token_type})
                Setting.objects.update_or_create(key="CREATED_AT_MOMO_ACCESS_TOKEN_DISBURSEMENT", defaults={"value": created_at_token})
                Setting.objects.update_or_create(key="EXPIRES_AT_MOMO_ACCESS_TOKEN_DISBURSEMENT", defaults={"value": expires_at_date})

                return {
                    "access_token": access_token,
                    "expires_in": expires_in,
                    "token_type": token_type,
                    "created_at_token": created_at_token,
                    "expires_at_date": expires_at_date
                }
            else:
                return None
        except requests.exceptions.RequestException as e:
            return None
    
def momoApiTokenIsExpired():
    try:
        EXPIRES_AT_MOMO_ACCESS_TOKEN_DISBURSEMENT = Setting.objects.get(key="EXPIRES_AT_MOMO_ACCESS_TOKEN_DISBURSEMENT")
    except Setting.DoesNotExist:
        getUserMomoToken()
        return False

    if EXPIRES_AT_MOMO_ACCESS_TOKEN_DISBURSEMENT:
        EXPIRES_AT_MOMO_ACCESS_TOKEN_DISBURSEMENT = datetime.strptime(EXPIRES_AT_MOMO_ACCESS_TOKEN_DISBURSEMENT.value, '%Y-%m-%d %H:%M:%S.%f')

        if datetime.now() > EXPIRES_AT_MOMO_ACCESS_TOKEN_DISBURSEMENT:
            return True
        else:
            return False
    else:
        return True

def  getToken():
    try:
        MOMO_ACCESS_TOKEN_DISBURSEMENT = Setting.objects.get(key="MOMO_ACCESS_TOKEN_DISBURSEMENT")
    except Setting.DoesNotExist:
        getUserMomoToken()
        MOMO_ACCESS_TOKEN_DISBURSEMENT = Setting.objects.get(key="MOMO_ACCESS_TOKEN_DISBURSEMENT")
        return MOMO_ACCESS_TOKEN_DISBURSEMENT.value
    
    if MOMO_ACCESS_TOKEN_DISBURSEMENT:
        if not momoApiTokenIsExpired():
            return MOMO_ACCESS_TOKEN_DISBURSEMENT.value
        else:
            getUserMomoToken()
            return Setting.objects.get(key="MOMO_ACCESS_TOKEN_DISBURSEMENT").value
    else:
        return None

def getHeader(token=None):
    if token is None:
        token = getToken()
    OCP_APIM_SUBSCRIPTION_KEY_DISBURSEMENT = Setting.objects.get(key="OCP_APIM_SUBSCRIPTION_KEY_DISBURSEMENT").value
    X_TARGET_ENVIRONMENT = CONFIG_MOMO_API.X_TARGET_ENVIRONMENT.value
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-Target-Environment": X_TARGET_ENVIRONMENT,
        "Ocp-Apim-Subscription-Key": OCP_APIM_SUBSCRIPTION_KEY_DISBURSEMENT
    }

def getMomoApiHeaders(referentId=None, withReferentId=True, withOcpApimSubscriptionKey=True):
    token = getToken()
    X_TARGET_ENVIRONMENT = CONFIG_MOMO_API.X_TARGET_ENVIRONMENT.value
    OCP_APIM_SUBSCRIPTION_KEY_DISBURSEMENT = Setting.objects.get(key="OCP_APIM_SUBSCRIPTION_KEY_DISBURSEMENT").value
    data = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-Target-Environment": X_TARGET_ENVIRONMENT,
    }
    if withReferentId and referentId:
        data["X-Reference-Id"] = referentId
    if withOcpApimSubscriptionKey:
        data["Ocp-Apim-Subscription-Key"] = OCP_APIM_SUBSCRIPTION_KEY_DISBURSEMENT

    return data

def getExternalIdUnique(length=9):
    characters = string.ascii_uppercase + string.digits
    while True:
        external_id = ''.join(random.choice(characters) for i in range(length))
        if not Transaction.objects.filter(external_id=external_id).exists() and not TontinierAbonnement.objects.filter(external_id=external_id).exists() and not Associate_carte.objects.filter(external_id=external_id).exists():
            return external_id

def getUniqueReferenceUuid():
    unique_uuid = uuid.uuid4()
    while True:
        if not Transaction.objects.filter(referenceId=unique_uuid).exists() and not TontinierAbonnement.objects.filter(referenceId=unique_uuid).exists() and not Associate_carte.objects.filter(referenceId=unique_uuid).exists():
            return unique_uuid