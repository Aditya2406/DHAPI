'''
    This file contains the data models for the application.
'''
from typing import Final


class ContactTypes:
    '''
        Contact Type
    '''
    EMAIL: Final[str] = "Email"
    PHONE: Final[str] = "Phone"
    ADDRESS: Final[str] = "Address"
    FAX: Final[str] = "Fax"
    WEBSITE: Final[str] = "Website"
    SOCIAL_MEDIA: Final[str] = "Social Media"
    OTHER: Final[str] = "Other"


class GenderTypes:
    '''
        Gender Types
    '''
    MALE: Final[int] = 0
    FEMALE: Final[int] = 1
    OTHERS: Final[int] = -1


class KYCDocumentTypes:
    '''
        KYC Document Types
    '''
    PASSPORT: Final[str] = "PASSPORT"
    DRIVING_LICENSE: Final[str] = "DRIVING_LICENSE"
    NATIONAL_ID: Final[str] = "NATIONAL_ID"
    BIRTH_CERTIFICATE: Final[str] = "BIRTH_CERTIFICATE"
    VOTER_ID: Final[str] = "VOTER_ID"
    GOVERNMENT_ISSUED_ID: Final[str] = "GOVERNMENT_ISSUED_ID"
