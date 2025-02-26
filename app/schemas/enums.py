from enum import Enum

class UserRole(int, Enum):
    """ Enum representing different user types. """
    ADMIN = 1
    SUB_ADMIN = 2
    USER = 3


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