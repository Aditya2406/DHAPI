'''
    vsys - Channel Model
'''
from enum import Enum
from dataclasses import dataclass, field
from typing import Final
from bson import ObjectId
import bson
from .base_data_model import BaseDataModel
from datetime import datetime


class BusinessChannelModes(Enum):
    '''
        Business Channel - Modes
    '''
    NOTSET = "NotSet"
    DEV = "Dev"
    TEST = "Test"
    LIVE = "Live"


class BusinessChannelTypes(Enum):
    '''
        Business Channel- Types
    '''
    NOTSET = "NOTSET"
    USSD = "USSD"
    WEB = "WEB"
    VENDOR_WEB = "VENDOR_WEB"
    RETAIL = "RETAIL"
    VENDOR_RETAIL = "VENDOR_RETAIL"


class ContactType(Enum):
    '''
        Artist Contact - Types
    '''
    EMAIL = "Email"
    NUMBER = "Number"


class ArtistGender:
    """
    Artist Gender
    """

    MALE: Final[int] = 0
    FEMALE: Final[int] = 1
    OTHERS: Final[int] = -1


class ArtistTypes:
    """
    Artist Types
    """
    # COUNTRY_ARTIST_MANAGER: Final[str] = "CAM"
    # PROVINCE_ARTIST_MANAGER: Final[str] = "PAM"
    # DISTRICT_Artist_MANAGER: Final[str] = "DAM"
    # COUMMUNE_Artist_MANAGER: Final[str] = "CMA"
    # SUPER_Artist: Final[str] = "SAG"
    FIELD_ARTIST: Final[str] = "FAG"


@dataclass()
class ArtistContact():
    '''
        Artist Contacts 
        //what will be the default of Type (default of CantactType)
    '''
    Type: str = field(default_factory=str)
    Contact: str = field(default_factory=str)
    IsPrimary: bool = field(default=False)
    IsPublic: bool = field(default=False)
    IsVerified: bool = field(default=False)
    IsActive: bool = field(default=False)


@dataclass()
class ArtistDataModel(BaseDataModel):
    '''
        Artist Model
    '''
    ArtistId: str = field(default_factory=str)
    ArtistName: str = field(default_factory=str)
    ArtistContact: str = field(default_factory=str)
    ArtistEmail: str = field(default_factory=str)
    Status: bool = field(default=False)
    Gender: int = field(default=ArtistGender.MALE)
    BirthDate: str = field(default_factory=str)
    Key: str = field(default_factory=str)
    ParentArtistId: ObjectId | None = field(default=None)
    ArtistType: str = field(default=ArtistTypes.FIELD_ARTIST)
    GeoLatitude: float | None = field(default=None)
    GeoLongitude: float | None = field(default=None)
    GeoLocation: str | None = field(default=None)


@dataclass()
class ArtistSessionDataModel(BaseDataModel):
    '''
        Artist Session Data Model

    '''
    SessionId: str = field(default_factory=str)
    ArtistId: str = field(default_factory=str)
    ArtistOId: bson.ObjectId | None = field(default=None)
    TokenFor: str = field(default_factory=str)
    TokenExpiry: datetime | None = field(default=None)
