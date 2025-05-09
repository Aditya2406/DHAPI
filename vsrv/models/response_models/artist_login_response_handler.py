'''
    Artist Auth Response Models
'''

from dataclasses import dataclass, field


@dataclass()
class ArtistLoginResponseModel():
    '''
        Channel Artist Login 
    '''
    Token: str = field(default_factory=str)
    ArtistId: str = field(default_factory=str)
    ArtistUserName: str = field(default_factory=str)
    ArtistFullName: str = field(default_factory=str)
    TokenValidTill: str = field(default_factory=str)
    TokenValidFor: str = field(default_factory=str)


@dataclass()
class ArtistAuthToken():
    '''
        Channel Artist Login 
    '''
    Token: str = field(default_factory=str)
    ArtistUserName: str = field(default_factory=str)
    TokenValidTill: str = field(default_factory=str)
    TokenValidFor: str = field(default_factory=str)
    TokenExpired: bool = field(default=False)
