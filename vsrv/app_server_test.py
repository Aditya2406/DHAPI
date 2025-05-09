'''
    Test Server Parameters 
'''
from vsrv import DatabaseCollections,class_constants
from vsrv.utils import config_utils
from vsrv.exceptions import ApplicationException, ExceptionReason, ExceptionSeverity

async def test_app_db_connect():
    '''
        Checks Database Connection by calling CollectionNames from Database
    '''
    try:
        db_conn = config_utils.app_db_connect()
        coll_names = await db_conn.list_collection_names()

        # Get DatabaseCollection Constants
        db_collections = class_constants(DatabaseCollections)

        # Check if all Collection names available in coll_names
        coll_not_found = []
        for coll_name in db_collections.values():
            if coll_name not in coll_names:
                coll_not_found.append(coll_name)

        if coll_not_found:
            msg = f'Database Connection Successful. Whereas Collection(s) Not Found: {coll_not_found}'
            raise ApplicationException(
                message=msg,
                reason=ExceptionReason.SYSTEM,
                severity=ExceptionSeverity.CRITICAL
            )

        return coll_names   ## Return Collection Names

    except ApplicationException as exc:
        raise exc
    except Exception as exc:
        raise ApplicationException(
            message=str(exc),
            exceptionObject=exc,
            reason=ExceptionReason.SYSTEM,
            severity=ExceptionSeverity.CRITICAL
        ) from exc
