from enum import Enum

class UserRole(str, Enum):
    """ Enum representing different user types. """
    ADMIN = "ADMIN"
    SUB_ADMIN = "SUB_ADMIN"
    USER = "USER"


class LogLevel(str, Enum):
    """ Enum representing different log levels. """

    INFO = "INFO"
    ERROR = "ERROR"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    DEBUG = "DEBUG"
    CRITICAL = "CRITICAL"


class ModelTypeEnum(str, Enum):
    """ Enum representing different service / model types. """

    DETECTION = "DETECTION"
    SEGMENTATION = "SEGMENTATION"
    CLASSIFICATION = "CLASSIFICATION"
    POSE = "POSE"


class ResponseTypes(int, Enum):
    """ Enum representing different status types. """
    FAILED = 0
    SUCCESS = 1


class ContactType(str, Enum):
    """ Enum representing different Contact types. """

    HOME = "HOME"
    WORK = "WORK"
    OTHER = "OTHER"


class CurrencyEnum(str, Enum):
    """ Enum representing different Contact types. """

    INR = "INR"
    USD = "USD"
    EUR = "EUR"


class FeatureDataType(str, Enum):
    """ Enum representing different data types of a Feature. """

    STRING = "STRING"
    NUMBER = "NUMBER"
    BOOLEAN = "BOOLEAN"


class SubscriptionPlans(str, Enum):
    """ Enum representing different subscription plan types. """

    BASIC = "BASIC"
    SILVER = "SILVER"
    GOLD = "GOLD"


class PaymentStatus(str, Enum):
    """ Enum representing different payment status. """

    CREATED = "created"
    AUTHORIZED = "authorized"
    CAPTURED = "captured"    
    REFUNDED = "refunded"    
    FAILED = "failed"


class ActivityTypeEnum(str, Enum):
    """ Enum representing different Activity types. """

    STORAGE_USAGE = "STORAGE_USAGE"
    IMAGE_USAGE = "IMAGE_USAGE"
    VIDEO_USAGE = "VIDEO_USAGE"