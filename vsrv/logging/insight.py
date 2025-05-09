'''
    vsrv - insight
'''
import concurrent
import concurrent.futures
import os
import logging
import logging.handlers
from typing import Mapping
from itertools import repeat
from vsrv.utils.config_utils import ConfigurationUtils


class SystemInsight():
    '''
        Application Insight Loging 
    '''
    __SystemLog__ = None

    @staticmethod
    def logger():
        '''
            System Logger
        '''
        if SystemInsight.__SystemLog__ is None:
            SystemInsight.__SystemLog__ = SystemLog()

        return SystemInsight.__SystemLog__


class SystemLog():
    '''
        System Logging
    '''

    __Logger__: logging.Logger | None = None
    __LogName__: str = ''
    # __Executor__ : concurrent.futures.ThreadPoolExecutor | None = None

    def __init__(self) -> None:
        '''
            Constructor
        '''
        if self.__Logger__ is None:
            # ? Get Log Name from Configuration
            log_name = "ARIS"
            self.__LogName__ = log_name

            # ? Application Logger required Initialization
            self.__Logger__ = logging.Logger(name=log_name, level=logging.DEBUG)
            # self.__Executor__ = concurrent.futures.ThreadPoolExecutor(max_workers=100, thread_name_prefix=log_name)

            # ? Shell Logging
            lshell = logging.StreamHandler()
            lshell.setLevel(level=logging.DEBUG)
            dash = ' '.join(list(repeat('-', 20)))
            lshell.terminator = f'\n{dash}\n'
            self.__Logger__.addHandler(lshell)

    def debug(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'DEBUG'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.debug("Houston, we have a %s", "thorny problem", exc_info=1)
        """
        if self.__Logger__ is not None:
            self._log_(logging.DEBUG, msg, args, **kwargs)

    def info(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'INFO'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.info("Houston, we have a %s", "interesting problem", exc_info=1)
        """
        if self.__Logger__ is not None:
            self._log_(logging.INFO, msg, args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'WARNING'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.warning("Houston, we have a %s", "bit of a problem", exc_info=1)
        """
        if self.__Logger__ is not None:
            self._log_(logging.WARNING, msg, args, **kwargs)

    def error(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'ERROR'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.error("Houston, we have a %s", "major problem", exc_info=1)
        """
        if self.__Logger__ is not None:
            self._log_(logging.ERROR, msg, args, **kwargs)

    def exception(self, msg, *args, exc_info=True, **kwargs):
        """
        Convenience method for logging an ERROR with exception information.
        """
        self.error(msg, *args, exc_info=exc_info, **kwargs)

    def log(self,
            level: int,
            msg: object,
            *args,
            **kwargs):
        """
        Log 'msg % args' with the integer severity 'level'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.log(level, "We have a %s", "mysterious problem", exc_info=1)
        """
        if self.__Logger__ is not None:
            if self.__Logger__.isEnabledFor(level=level):
                self._log_(logging.INFO, msg, args, **kwargs)

    def _log_(self,
              level: int,
              msg: object,
              args,
              exc_info=None,
              stack_info: bool = False,
              stacklevel: int = 1,
              extra: Mapping[str, object] | None = None):
        '''
            Log Write 
        '''
        if self.__Logger__ is not None:
            if self.__Logger__.isEnabledFor(level=level):
                with concurrent.futures.ThreadPoolExecutor(max_workers=100, thread_name_prefix=self.__LogName__) as __executor__:
                    __executor__.submit(
                        self.__Logger__._log, level, msg, args, exc_info=exc_info, extra=extra, stack_info=stack_info, stacklevel=stacklevel
                    )
