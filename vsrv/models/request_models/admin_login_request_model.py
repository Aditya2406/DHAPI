'''
    Admin Login Request Models
'''

from dataclasses import dataclass, field


@dataclass
class AdminLoginRequestModel():
    '''
        Admin Create Request Model
    '''
    Username: str = field(default_factory=str)
    Password: str = field(default_factory=str)
    SessionId: str = field(default_factory=str)
