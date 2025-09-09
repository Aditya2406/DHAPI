'''
    Track Request Models
'''
from dataclasses import dataclass, field
from typing import List, Optional

from vsrv.models.data_models.base_data_model import BaseDataModel


@dataclass
class PersonInfo:
    '''
        Person Information Model (for singers, writers, composers)
    '''
    Name: str = field(default_factory=str)
    ProfileUrl: str = field(default_factory=str)


@dataclass
class TrackMeta:
    '''
        Track Metadata Model
    '''
    Singer: List[PersonInfo] = field(default_factory=list)
    MusicBy: List[PersonInfo] = field(default_factory=list)
    WrittenBy: List[PersonInfo] = field(default_factory=list)
    Lyrics: str = field(default_factory=str)
    Language: str = field(default_factory=str)
    CoverImg: str = field(default_factory=str)


@dataclass
class TrackModel(BaseDataModel):
    '''
        Track Create Request Model
    '''
    Title: str = field(default_factory=str)
    ReleaseId: str = field(default_factory=str)
    Undertaking: str = field(default_factory=str)
    IsSigned: bool = field(default=False)
    IsApproved: bool = field(default=False)
    Status: bool = field(default=True)
    ArtistId: str = field(default_factory=str)
    Track: str = field(default_factory=str)
    Meta: Optional[TrackMeta] = field(default=None)
