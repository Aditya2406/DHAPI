'''
    Artist Response Models
'''

from dataclasses import dataclass, field
from typing import Any, List


@dataclass()
class NewArtistsResponseModel():
    '''
        Create Artist - Response Model
    '''
    ArtistId: str = field(default_factory=str)
    ArtistUserName: str = field(default_factory=str)
    Status: bool = field(default_factory=bool)


@dataclass()
class AgentsResponseModel():
    '''
        Player Tickets - Response Model
    '''
    PageNumber: int = -1
    PageSize: int = -1
    TotalPages: int = -1
    Artists: List[Any] = field(default_factory=list)
