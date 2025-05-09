'''
    Pagination Utils
'''    
from vsrv.net.base_handlers import BaseRequestHandler
from vsrv.exceptions import ApplicationException, ExceptionSeverity, ExceptionReason
from vsrv.models.util_models.pagination_models import PagniationModel

@staticmethod
def data_pagination(handler:BaseRequestHandler, page_size:int=10, page_number:int=1, log_msg_heading:str="") -> PagniationModel:
    '''
        Pagination
    '''
    __page_size_key__ = ['PAGESIZE']
    __page_number_key__ = ['PAGENUMBER', 'PAGENO']

    __page_size__ = page_size
    __page_number__ = page_number
    __record_skip__ = 0
    __record_limit__ = 0
    try:
        # ? Check Paging Parameters
        if len(handler.request.arguments) > 0:
            has_page_size = any(akey in __page_size_key__ for akey in [K.upper() for K in handler.request.arguments.keys()])
            has_page_number = any(akey in __page_number_key__ for akey in [K.upper() for K in handler.request.arguments.keys()])

            # Check Page Size
            if has_page_size > 0:
                _page_size = next((handler.request.arguments[K] for K in handler.request.arguments.keys() if K.upper() in __page_size_key__), None)
                try:
                    if _page_size is not None:
                        __page_size__ = int(bytes.decode(_page_size[0]))
                    else:
                        __page_size__ = 10

                    __page_size__ = __page_size__ if __page_size__ > 0 else 10     # Making Default Page Size if PageSize Given Below 10
                except Exception as exc:
                    raise ApplicationException(
                        message=f"{log_msg_heading} : Invalid Page Size",
                        severity=ExceptionSeverity.MODERATE,
                        reason=ExceptionReason.USER,
                        exceptionObject=exc
                    ) from exc

            # Check Page Number
            if has_page_number > 0:
                _page_number = next((handler.request.arguments[K] for K in handler.request.arguments.keys() if K.upper() in __page_number_key__), None)
                try:
                    if _page_number is not None:
                        __page_number__ = int(bytes.decode(_page_number[0]))
                    else:
                        __page_number__ = 1

                    __page_number__ = __page_number__ if __page_number__ > 1 else 1     # Making Default Page No if Page No Given Below 1

                except Exception as exc:
                    raise ApplicationException(
                        message=f"{log_msg_heading} : Invalid Page Size",
                        severity=ExceptionSeverity.MODERATE,
                        reason=ExceptionReason.USER,
                        exceptionObject=exc
                    ) from exc

        # ? Record Paging  Calculation
        __record_skip__ = (__page_number__-1) * __page_size__
        __record_limit__ = __page_size__

        return PagniationModel(
            PageSize=__page_size__,
            PageNumber=__page_number__,
            RecordSkip=__record_skip__,
            RecordLimit=__record_limit__
        )

    except ApplicationException as aexc:
        raise aexc

    except Exception as exc:
        raise exc
