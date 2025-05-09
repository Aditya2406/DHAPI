'''
    vsys - Base Data Model
'''
from datetime import datetime
from dataclasses import dataclass, field, asdict, fields, is_dataclass
from typing import get_origin
import bson
import bson.objectid
from vsrv.exceptions import ApplicationException, ExceptionSeverity, ExceptionReason


@dataclass
class BaseDataModel():
    '''
        Base Data Model
    '''
    _id: bson.ObjectId | None = field(default=None)
    Created: datetime | None = field(default=None)
    CreatedStr: str | None = field(default=None)
    Updated: datetime | None = field(default=None)
    UpdatedStr: str | None = field(default=None)
    Deleted: bool = field(default=False)

    def set_id(self, _new_id: bson.ObjectId):
        '''
            Set ID
        '''
        if isinstance(_new_id, str):
            self._id = bson.ObjectId(_new_id)
            # --> Set ID
        elif isinstance(_new_id, bson.ObjectId):
            self._id = _new_id
            # --> Set ID
        else:
            raise ApplicationException(
                severity=ExceptionSeverity.CRITICAL,
                reason=ExceptionReason.SYSTEM,
                message="ID should be a valid ObjectId or a String representation of ObjectId"
            )
            # <-- Invalid ID

    def get_id(self) -> bson.ObjectId | None:
        '''
            Get ID
        '''
        if self._id is None:
            return None
            # --> Return None
        elif isinstance(self._id, str):
            return bson.ObjectId(self._id)
            # --> Return ID
        elif isinstance(self._id, bson.ObjectId):
            return self._id
            # --> Return ID
        else:
            return None
            # --> Return None

    def get_id_str(self) -> str:
        '''
            Get ID as String
        '''
        if self._id is None:
            return ''
        else:
            return str(self._id)
            # --> Return ID as String

    def as_dict_unsecured(self) -> dict:
        '''
            Convert to Dictionary
        '''
        return asdict(self)
        # --> Return Full Dictionary

    def as_dict(self) -> dict:
        '''
            Convert to Dictionary
        '''
        _dict = self.as_dict_unsecured()
        for _field in fields(self):
            field_type = _field.type

            if not isinstance(field_type, type):
                field_type = get_origin(field_type) or field_type

            # ! is BaseDataModel
            if isinstance(field_type, type) and issubclass(field_type, BaseDataModel) and is_dataclass(field_type):
                # ! value is not None
                if _dict[_field.name] is not None:
                    # ! get field value
                    __val__ = getattr(self, _field.name)
                    __val_safe__ = __val__.as_dict()
                    _dict[_field.name] = __val_safe__

            # ! is_secured is a metadata field from BaseFieldMeta class
            if _field.metadata.get('is_secured', False):
                _dict.pop(_field.name)

        return _dict
        # --> Return Safe Dictionary


@dataclass
class BaseFieldMeta:
    '''
        BaseFieldMeta
    '''
    is_secured: bool = field(default=False)

    def as_dict(self) -> dict:
        '''
            Convert to Dictionary
        '''
        return asdict(self)
        # --> Return Full Dictionary
