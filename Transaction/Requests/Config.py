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
    OCP_APIM_SUBSCRIPTION_KEY = CONFIG_MOMO_API.OCP_APIM_SUBSCRIPTION_KEY.value
    X_REFERENCE_ID = CONFIG_MOMO_API.X_REFERENCE_ID.value

    OCP_APIM_SUBSCRIPTION_KEY, create = Setting.objects.get_or_create(key="OCP_APIM_SUBSCRIPTION_KEY", defaults={"value": OCP_APIM_SUBSCRIPTION_KEY})
    OCP_APIM_SUBSCRIPTION_KEY = OCP_APIM_SUBSCRIPTION_KEY.value

    X_REFERENCE_ID, create = Setting.objects.get_or_create(key="X_REFERENCE_ID", defaults={"value": X_REFERENCE_ID})
    X_REFERENCE_ID = X_REFERENCE_ID.value
    
    return OCP_APIM_SUBSCRIPTION_KEY, X_REFERENCE_ID

def getApiKey():
    OCP_APIM_SUBSCRIPTION_KEY, X_REFERENCE_ID = getAppOCPAPIM_X_REFERENCE_ID()
    BASE_API_URL = CONFIG_MOMO_API.BASE_URL.value + CONFIG_MOMO_API.VERSION.value + "/apiuser/" + X_REFERENCE_ID + "/apikey"
    headers = {
        "Ocp-Apim-Subscription-Key": OCP_APIM_SUBSCRIPTION_KEY,
    }

    response = requests.post(BASE_API_URL, headers=headers)
    if response and response.status_code == 201:
        api_key = response.json().get("apiKey")
        Setting.objects.update_or_create(key="API_KEY", defaults={"value": api_key})
        return api_key
    else:
        return None

def getUserMomoToken():
    try:
        OCP_APIM_SUBSCRIPTION_KEY = Setting.objects.get(key="OCP_APIM_SUBSCRIPTION_KEY")
        X_REFERENCE_ID = Setting.objects.get(key="X_REFERENCE_ID")
        API_KEY = Setting.objects.get(key="API_KEY") 
    except Setting.DoesNotExist:
        OCP_APIM_SUBSCRIPTION_KEY, X_REFERENCE_ID = getAppOCPAPIM_X_REFERENCE_ID()
        API_KEY = getApiKey()

    if OCP_APIM_SUBSCRIPTION_KEY and X_REFERENCE_ID and API_KEY:
        OCP_APIM_SUBSCRIPTION_KEY = OCP_APIM_SUBSCRIPTION_KEY.value
        X_REFERENCE_ID = X_REFERENCE_ID.value
        API_KEY = API_KEY.value


        BASE_API_URL = CONFIG_MOMO_API.BASE_URL.value + "collection/token/"
        auth_header = base64.b64encode(f"{X_REFERENCE_ID}:{API_KEY}".encode('utf-8')).decode('utf-8')

        headers = {
            "Ocp-Apim-Subscription-Key": OCP_APIM_SUBSCRIPTION_KEY,
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

                Setting.objects.update_or_create(key="MOMO_ACCESS_TOKEN", defaults={"value": access_token})
                Setting.objects.update_or_create(key="MOMO_ACCESS_TOKEN_EXP", defaults={"value": expires_in})
                Setting.objects.update_or_create(key="MOMO_TOKEN_TYPE", defaults={"value": token_type})
                Setting.objects.update_or_create(key="CREATED_AT_MOMO_ACCESS_TOKEN", defaults={"value": created_at_token})
                Setting.objects.update_or_create(key="EXPIRES_AT_MOMO_ACCESS_TOKEN", defaults={"value": expires_at_date})

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
        EXPIRES_AT_MOMO_ACCESS_TOKEN = Setting.objects.get(key="EXPIRES_AT_MOMO_ACCESS_TOKEN")
    except Setting.DoesNotExist:
        getUserMomoToken()
        return False

    if EXPIRES_AT_MOMO_ACCESS_TOKEN:
        EXPIRES_AT_MOMO_ACCESS_TOKEN = datetime.strptime(EXPIRES_AT_MOMO_ACCESS_TOKEN.value, '%Y-%m-%d %H:%M:%S.%f')

        if datetime.now() > EXPIRES_AT_MOMO_ACCESS_TOKEN:
            return True
        else:
            return False
    else:
        return True

def getToken():
    try:
        MOMO_ACCESS_TOKEN = Setting.objects.get(key="MOMO_ACCESS_TOKEN")
    except Setting.DoesNotExist:
        getUserMomoToken()
        MOMO_ACCESS_TOKEN = Setting.objects.get(key="MOMO_ACCESS_TOKEN")
        return MOMO_ACCESS_TOKEN.value
    
    if MOMO_ACCESS_TOKEN:
        if not momoApiTokenIsExpired():
            return MOMO_ACCESS_TOKEN.value
        else:
            getUserMomoToken()
            return Setting.objects.get(key="MOMO_ACCESS_TOKEN").value
    else:
        return None

def getHeader(token=None):
    if token is None:
        token = getToken()
    OCP_APIM_SUBSCRIPTION_KEY = Setting.objects.get(key="OCP_APIM_SUBSCRIPTION_KEY").value
    X_TARGET_ENVIRONMENT = CONFIG_MOMO_API.X_TARGET_ENVIRONMENT.value
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-Target-Environment": X_TARGET_ENVIRONMENT,
        "Ocp-Apim-Subscription-Key": OCP_APIM_SUBSCRIPTION_KEY
    }

def getMomoApiHeaders(referentId=None, withReferentId=True, withOcpApimSubscriptionKey=True):
    token = getToken()
    X_TARGET_ENVIRONMENT = CONFIG_MOMO_API.X_TARGET_ENVIRONMENT.value
    OCP_APIM_SUBSCRIPTION_KEY = Setting.objects.get(key="OCP_APIM_SUBSCRIPTION_KEY").value
    data = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-Target-Environment": X_TARGET_ENVIRONMENT,
    }
    if withReferentId and referentId:
        data["X-Reference-Id"] = referentId
    if withOcpApimSubscriptionKey:
        data["Ocp-Apim-Subscription-Key"] = OCP_APIM_SUBSCRIPTION_KEY

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