'''
    Channel Request Models
'''

from dataclasses import dataclass, field


@dataclass
class ArtistCreateRequestModel():
    '''
        Artist Create Request Model
    '''
    ArtistId: str = field(default_factory=str)
    ArtistName: str = field(default_factory=str)
    ArtistContact: str = field(default_factory=str)
    Gender: int = field(default_factory=int)
    BirthDate: str = field(default_factory=str)
    Status: bool = field(default=False)
    GeoLatitude: float | None = field(default=None)
    GeoLongitude: float | None = field(default=None)
    GeoLocation: str | None = field(default=None)
