from enum import Enum

class AccountTypeEnum(Enum):
    ADMIN = 'ADMIN'
    SIMPLE = 'SIMPLE'
    TONTINE = 'TONTINE'

class StatusAbonnementEnum(Enum):
    IN_PROGRESS = 'IN_PROGRESS'
    FINISH = 'FINISH'
    NO_VALIDATE = 'NO_VALIDATE'

class StatusGroupeEnum(Enum):
    INSCRIPTION = 'INSCRIPTION'
    IN_PROGRESS = 'IN_PROGRESS'
    COMPLETED = 'COMPLETED'
    CANCELLED = 'CANCELLED'

class InvitationStatusEnum(Enum):
    PENDING = 'PENDING'
    ACCEPTED = 'ACCEPTED'
    REJECTED = 'REJECTED'
    EXPIRED = 'EXPIRED'
    CANCELLED = 'CANCELLED'

class StatusTontinierEnum(Enum):
    COLLECTED = 'COLLECTED'
    REQUEST_SENT = 'REQUEST_SENT'
    REQUEST_IN_PROGRESS = 'REQUEST_IN_PROGRESS'
    NOT_COLLECTED = 'NOT_COLLECTED'

class TontineTypeEnum(Enum):
    CARTE = 'CARTE'
    GROUPE = 'GROUPE'

class Period(Enum):
    DAY = 'DAY'
    WEEK = 'WEEK'
    MONTH = 'MONTH'

class NotificationType(Enum):
    ALERT_CONTRIBUTION = 'ALERT_CONTRIBUTION'
    ALERT_PAYMENT = 'ALERT_PAYMENT'
    ALERT_INVITATION = 'ALERT_INVITATION'
    ALERT_INTEGRATION = 'ALERT_INTEGRATION'
    ALERT_CLOTURE = 'ALERT_CLOTURE'

class StatusTransactionEnum(Enum):
    PENDING = 'PENDING'
    SUCCESSFUL = 'SUCCESSFUL'
    FAILED = 'FAILED'
    EXPIRED = 'EXPIRED'
    PENDING_CONFIRMATION = 'PENDING_CONFIRMATION'
    REJECTED = 'REJECTED'
    CANCELLED = 'CANCELLED'
    PROCESSING = 'PROCESSING'
    REFUNDED = 'REFUNDED'
    UNKNOWN = 'UNKNOWN'

class TypeTransactionEnum(Enum):
    CONTRIBUTION = 'CONTRIBUTION'
    COLLECTED = 'COLLECTED'

class TypeRuleEnum(Enum):
    CARTES = 'CARTES'
    GROUPES = 'GROUPES'
    COMMUN = 'COMMUN'

class AbonnementEnum(Enum):
    SIMPLE = {
        'name': 'Simple',
        'sale_price': 1000,
        'can_create_groupe': False,
        'can_create_carte': True,
        'duration_days': 365
    }
    GROUPE = {
        'name': 'Groupe',
        'sale_price': 1500,
        'can_create_groupe': True,
        'can_create_carte': False,
        'duration_days': 365
    }
    PREMIUM = {
        'name': 'Premium',
        'sale_price': 2000,
        'can_create_groupe': True,
        'can_create_carte': True,
        'duration_days': 365
    }

class CountryEnum(Enum):
    BENIN = {
        'name': 'Benin',
        'code': 'BJ',
        'phone_code': '+229'
    }
    TOGO = {
        'name': 'Togo',
        'code': 'TG',
        'phone_code': '+228'
    }
    COTE_DIVOIRE = {
        'name': 'Cote d\'Ivoire',
        'code': 'CI',
        'phone_code': '+225'
    }

class AbonnementTransactionStatusEnum(Enum):
    PAYE = 'PAYE'
    NO_PAYE = 'NO_PAYE'

class daysEnum(Enum):
    MON = {
        'fr': 'LUNDI',
        'en': 'MONDAY'
    }
    TUE = {
        'fr': 'MARDI',
        'en': 'TUESDAY'
    }
    WED = {
        'fr': 'MERCREDI',
        'en': 'WEDNESDAY'
    }
    THU = {
        'fr': 'JEUDI',
        'en': 'THURSDAY'
    }
    FRI = {
        'fr': 'VENDREDI',
        'en': 'FRIDAY'
    }
    SAT = {
        'fr': 'SAMEDI',
        'en': 'SATURDAY'
    }
    SUN = {
        'fr': 'DIMANCHE',
        'en': 'SUNDAY'
    }