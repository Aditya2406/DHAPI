'''
    Realese Request Models
'''

from dataclasses import dataclass, field
import token


@dataclass
class RealeseCreateRequestModel():
    '''
        Realese Create Request Model
    '''
    RealeseName: str = field(default_factory=str)
    ReleaseType: int = field(default_factory=int)
    token: str = field(default_factory=str)
    Status: bool = field(default=False)
    GeoLatitude: float | None = field(default=None)
    GeoLongitude: float | None = field(default=None)
    GeoLocation: str | None = field(default=None)
