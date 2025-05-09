'''
    vsys - JSON Utilities
'''
from typing import Any, Type
import enum
import json
import inspect
from vsrv.utils import encoder_utils
from vsrv.exceptions import ApplicationException, ExceptionSeverity

class JSONHelper():
    '''
        JSON Helper
    '''

    @staticmethod
    def odump(obj:Any,indent:int=2):
        '''
            Object Dump
        '''
        serialized = json.dumps(obj,cls=encoder_utils.ObjectEncoder,indent=indent)
        return serialized

    @staticmethod
    def odump_dict(obj:Any):
        '''
            Object Dump as Dictionary
        '''
        json_str = JSONHelper.odump(obj=obj)
        j = json.loads(json_str)
        return j

    @staticmethod
    def parse(json_obj:Any,cls_type:Type):
        '''
            Parse JSON Object to Class Type
        '''
        target = cls_type()
        try:
            props = [P for P in dir(target) if not P.startswith("_")]
            for prop in props:
                property_name = prop
                property_type = type(getattr(target,prop))
                if not inspect.ismethod(getattr(target,prop)) or inspect.isfunction(getattr(target,prop)):
                    if isinstance(property_type,enum.EnumMeta) :
                        if property_name in json_obj.keys():
                            setattr(target,prop, getattr(property_type,json_obj[property_name]))
                    elif property_type is str or property_type is int or property_type is list:
                        #if json_obj.keys().__contains__(property_name):
                        if property_name in json_obj.keys():
                            setattr(target,prop, json_obj[property_name])
                    #elif json_obj.keys().__contains__(property_name):
                    elif property_name in json_obj.keys():
                        property_value = json_obj[property_name]
                        filled_property = JSONHelper.parse(property_value,property_type)
                        setattr(target,prop, filled_property)
            return target
        except KeyError as exp:
            raise ApplicationException(
                severity=ExceptionSeverity.SHOW_STOPPER,
                message=f"JSON Parsing Failed, No Key Found {exp.args}",
                exceptionObject=exp
            ) from exp
        except Exception as exp:
            raise ApplicationException(
                severity=ExceptionSeverity.SHOW_STOPPER,
                message="JSON Parsing Failed",
                exceptionObject=exp
            ) from exp
