'''
    Pagination Models
'''

from dataclasses import dataclass, field

@dataclass
class PagniationModel:
    '''
        Pagination Model
    '''
    PageSize:int = field(default=10)
    PageNumber:int = field(default=1)
    RecordSkip:int = field(default=0)
    RecordLimit:int = field(default=0)
    TotalRecords:int = field(default=0)
    TotalPages:int = field(default=0)
