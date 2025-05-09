'''
    vsrv - Utilities - Encoders
'''
from typing import Any
import json
import enum
import datetime
import bson
import bson.objectid
from colorama import Fore

class ObjectEncoder(json.JSONEncoder):
    '''
        Object Encoder
    '''
    def default(self, o: Any) -> Any:
        if o.__class__.__base__ == enum.Enum:
            return o.name
        elif o.__class__ == datetime.datetime or o.__class__ == datetime.date \
            or o.__class__ == datetime.time or o.__class__ == datetime.timedelta \
            or o.__class__ == datetime.timezone or o.__class__ == datetime.tzinfo:
            return str(o)
        elif o.__class__ == bson.objectid.ObjectId:
            return str(o)
        elif isinstance(o,bytes):
            return bytes.decode(o)
        else:
            try:
                return o.__dict__
            except Exception as exc:
                print(Fore.YELLOW + 'Exception')
                print(exc)
                return str(o)
