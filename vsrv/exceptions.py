'''
    vsrv - Exception Classes
'''
from http import HTTPStatus
from typing import Any
from enum import Enum
from .net import body


class ExceptionSeverity(Enum):
    '''
        vsrv - Application Exception Severity Level
    '''
    SHOW_STOPPER = 1
    CRITICAL = 2
    HIGH = 3
    MODERATE = 4
    LOW = 5


class ExceptionReason(Enum):
    '''
        vsrv - Application Exception Reason
        Tells Side for Exception Reason
    '''
    USER = 1
    SYSTEM = 10
    INTEGRATION = 20


class ApplicationException(Exception):
    '''
        vsrv - Application Exception
    '''

    def __init__(self, severity: ExceptionSeverity = ExceptionSeverity.LOW, reason: ExceptionReason = ExceptionReason.USER, message: str = "", exceptionObject: Any = None, httpStatus: int = HTTPStatus.BAD_REQUEST):
        self.HttpStatus = httpStatus
        self.Severity = severity
        self.Reason = reason
        self.Message = message
        self.ExceptionObject = exceptionObject

    def response(self) -> dict[str, Any]:
        '''
            Application Exception - HTTP Body (vSys.http.Body.HTTPBody) Response
        '''
        return body.HTTPBody(
            status_code_=self.HttpStatus,
            status_message_=self.Message,
            data={}).body()

    def __str__(self) -> str:
        return f'{str(self.Severity)} : {str(self.Reason)} : {self.Message}'
