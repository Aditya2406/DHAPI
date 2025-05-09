'''
    Class Utilities
'''
import bson
import dacite


def class_constants(cls):
    '''
        return Class Constants
    '''
    return {name: value for name, value in cls.__dict__.items() if name.isupper()}


def dict_to_dataclass(cls, data: dict):
    '''
        Convert Dict to Class
    '''
    # ? Convert _id to ObjectId
    if "_id" in data.keys():
        __value__ = data["_id"]
        if isinstance(__value__, str):
            data["_id"] = bson.ObjectId(__value__)

    return dacite.from_dict(cls, data)
