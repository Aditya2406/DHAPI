'''
    Admindmin Auth Response Models
'''

from dataclasses import dataclass, field


@dataclass()
class AdminsLoginResponseModel():
    '''
        Channel admin Login 
    '''
    Token: str = field(default_factory=str)
    AdminId: str = field(default_factory=str)
    AdminUserName: str = field(default_factory=str)
    AdminFullName: str = field(default_factory=str)
    TokenValidTill: str = field(default_factory=str)
    TokenValidFor: str = field(default_factory=str)


@dataclass()
class AdminsAuthToken():
    '''
        Channel admin Login 
    '''
    Token: str = field(default_factory=str)
    AdminUserName: str = field(default_factory=str)
    TokenValidTill: str = field(default_factory=str)
    TokenValidFor: str = field(default_factory=str)
    TokenExpired: bool = field(default=False)
