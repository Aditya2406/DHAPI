'''
    Models Package
'''

import dataclasses


class StatusCodeModel:
    '''
        Status Code Model
    '''
    def __init__(self, code:int, message:str) -> None:
        self.__code__ = code
        self.__message__ = message

    @property
    def Code(self):
        '''
            Status Code
        '''
        return self.__code__

    @property
    def Message(self):
        '''
            Status Message
        '''
        return self.__message__
