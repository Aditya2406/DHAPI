'''
    Release Request Models
'''
from dataclasses import dataclass, field
from typing import List

import bson
from vsrv.models.data_models.base_data_model import BaseDataModel


@dataclass
class TrackInfo:
    '''
        Track Information Model
    '''
    TrackId: str = field(default_factory=str)
    IsQATested: bool = field(default=False)
    IsApproved: bool = field(default=False)
    IsDistributed: bool = field(default=False)


@dataclass
class ReleaseLink:
    '''
        Release Link Model
    '''
    Platform: str = field(default_factory=str)
    Link: str = field(default_factory=str)


@dataclass
class ReleaseDataModel(BaseDataModel):
    '''
        Release Create Request Model
    '''
    Title: str = field(default_factory=str)
    ReleaseType: int = field(default_factory=int)
    Tracks: List[TrackInfo] = field(default_factory=list)
    Undertaking: str = field(default_factory=str)
    IsSigned: bool = field(default=False)
    IsApproved: bool = field(default=False)
    Status: bool = field(default=True)
    ArtistId: bson.ObjectId | None = field(default=None)
    ReleaseLinks: List[ReleaseLink] = field(default_factory=list)
    StatusCode: int = field(default_factory=int)
