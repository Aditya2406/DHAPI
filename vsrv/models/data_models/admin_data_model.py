'''
    Admin Model
'''
from dataclasses import dataclass, field
from datetime import datetime
from .base_data_model import BaseDataModel


@dataclass()
class AdminDataModel(BaseDataModel):
    '''
        Admin Model
    '''
    AdminId: str = field(default_factory=str)
    AdminName: str = field(default_factory=str)
    AdminContact: str = field(default_factory=str)
    Status: bool = field(default=False)
    Key: str = field(default_factory=str)


@dataclass()
class AdminSessionDataModel(BaseDataModel):
    '''
        Admin Session Data Model

    '''
    SessionId: str = field(default_factory=str)
    AdminId: str = field(default_factory=str)
    TokenFor: str = field(default_factory=str)
    TokenExpiry: datetime | None = field(default=None)
